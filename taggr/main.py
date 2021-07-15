import csv
import io
import os
import tempfile

import treepoem
from PIL import Image, ImageDraw, ImageFont
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file
)
from flask import current_app as app
from square.client import Client

from taggr.auth import login_required

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def index():
    if 's' in request.args:
        s = request.args.get('s')
        client = Client(
            access_token=g.user['square_api_key'],
            environment='production', )
        catalog_api = client.catalog
        result = catalog_api.search_catalog_items(
            body={
                "text_filter": "\"" + s + "\"",
            }
        )
        if result.is_success():
            # Check for results
            if 'items' not in result.body:
                error = "No Items Found."
                flash(error)
                return render_template('main/index.html')
            # See if multiple items were found
            if len(result.body["items"]) > 1:
                return render_template('main/select_item.html', items=result.body['items'])
            # Select the only item returned
            item = result.body["items"][0]
            # see if the item has more than one variation
            if len(item["item_data"]["variations"]) > 1:
                # Look for an exact match for the SKU
                for variation in item["item_data"]["variations"]:
                    if 'sku' in variation["item_variation_data"]:
                        if s == variation["item_variation_data"]["sku"]:
                            return redirect(url_for('main.get_item', item_id=variation["id"]))
                return render_template('main/select_item.html', items=result.body['items'])
            else:
                return redirect(url_for('main.get_item', item_id=item["item_data"]["variations"][0]["id"]))

    return render_template('main/index.html')


@bp.route('/item/<item_id>')
@login_required
def get_item(item_id):
    client = Client(
        access_token=g.user['square_api_key'],
        environment='production', )
    catalog_api = client.catalog
    inventory_api = client.inventory
    result = catalog_api.retrieve_catalog_object(
        object_id=item_id,
        include_related_objects=True)
    square_item = None
    square_variation = None
    inventory = 0
    if result.is_success():
        square_item = result.body["related_objects"][0]
        square_variation = result.body["object"]
        inventory_result = inventory_api.retrieve_inventory_count(
            catalog_object_id=square_variation["id"]
        )
        if inventory_result.is_success():
            for count in inventory_result.body["counts"]:
                inventory += int(count["quantity"])
    return render_template('main/item.html', item=square_item, variation=square_variation, inventory=inventory)


@bp.route('/image/30333.png')
@login_required
def get_image():
    # Load GET Variables
    name = request.args.get("name")
    price = request.args.get("price")
    sku = request.args.get("sku")

    # Format price
    price = float(price) / 100
    price = "${:,.2f}".format(price)

    # Create Image
    w, h = (300, 150)
    margin = 10
    img = Image.new('1', (w, h), color=1)
    d = ImageDraw.Draw(img)

    # Set Fonts
    title_font = ImageFont.truetype(app.root_path + '/glabel/OpenSans-SemiBold.ttf', 15)
    price_font = ImageFont.truetype(app.root_path + '/glabel/OpenSans-SemiBold.ttf', 55)

    # Calculate Text Position
    title_size_w, title_size_h = d.textsize(name, font=title_font)
    price_size_w, price_size_h = d.textsize(price, font=price_font)

    # Create Text
    d.text(((w - title_size_w) / 2, ((h / 2 - title_size_h) / 2) + margin), name, font=title_font, fill=0)
    d.text((((w - (w / 4)) - price_size_w) / 2, ((h - margin) - price_size_h)), price, font=price_font, fill=0)

    # Create Barcode
    barcode = treepoem.generate_barcode(barcode_type='datamatrix', data=sku)
    bc_width, bc_height = barcode.size
    img.paste(barcode.convert('1'), (w - margin - bc_width, h - margin - bc_height))

    # Create File in Memory
    file_object = io.BytesIO()
    img.save(file_object, 'PNG')
    file_object.seek(0)
    return send_file(file_object, mimetype="image/png")


@bp.route('/print')
@login_required
def print_tag():
    # Load GET Variables
    name = request.args.get("name")
    price = request.args.get("price")
    sku = request.args.get("sku")
    qty = request.args.get("qty")
    item_id = request.args.get("item_id")

    # Format price
    price = float(price) / 100
    price = "${:,.2f}".format(price)

    # Get Temp File for CSV
    csv_handle, csv_filepath = tempfile.mkstemp(suffix=".csv")

    # Save the CSV that will be read by GLabel
    csv_data = [['SKU', 'NAME', 'PRICE'], [sku, name, price]]
    with os.fdopen(csv_handle, 'w') as f:
        write = csv.writer(f)
        write.writerows(csv_data)

    # Get Temp File for PS Output
    ps_handle, ps_file_path = tempfile.mkstemp(suffix=".ps")

    # Run GLabel command to generate output
    if int(qty) > 1:
        cmd = "glabels-3-batch --input=" + csv_filepath + " --output=" + ps_file_path + " --copies=" + str(qty) + " " + app.root_path + "/glabel/DYMO30333.glabels"
    else:
        cmd = "glabels-3-batch --input=" + csv_filepath + " --output=" + ps_file_path + " " + app.root_path + "/glabel/DYMO30333.glabels"
    returned_value = os.system(cmd)

    # Check that it ran ok
    if returned_value == 0:
        # Print the output
        cmd = "lp -d " + str(g.user['dymo_printer_name']) + " " + ps_file_path
        returned_value = os.system(cmd)
        # Check that it printed ok
        if returned_value == 0:
            flash("Printing Complete.")
            os.remove(csv_filepath)
            os.remove(ps_file_path)
    return redirect(url_for('main.get_item', item_id=item_id))
