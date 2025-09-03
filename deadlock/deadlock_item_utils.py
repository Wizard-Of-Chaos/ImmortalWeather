import requests
from PIL import Image, PngImagePlugin
import os
import io

ITEM_IMG_PATH = "deadlock/item_img_buffer/"
DEADLOCK_API_URL = "https://api.deadlock-api.com/v1"

__ITEMS__ = { }
def __item_setup__():
    item_req = requests.get("https://assets.deadlock-api.com/v2/items/by-type/upgrade").json()
    for item in item_req:
        __ITEMS__[item["id"]] = item
__item_setup__()

# ITEMS = requests.get("https://assets.deadlock-api.com/v2/items/by-type/upgrade").json()

def get_item(id: int):
    if id in __ITEMS__:
        return __ITEMS__[id]
    return None

def is_upgrade(id: int) -> bool:
    if get_item(id):
        return True
    return False

def get_item_img(id: int) -> PngImagePlugin.PngImageFile:
    item = get_item(id)
    if item == None:
        print("item get failed")
        return
    data = requests.get(item["shop_image_small"]).content
    return Image.open(io.BytesIO(data))

def get_inventory_images(data) -> list[PngImagePlugin.PngImageFile]:
    ret = []
    for item in data:
        if item["sold_time_s"] != 0:
            continue
        id = item["item_id"]
        if is_upgrade(id):
            ret.append(get_item_img(id))
    return ret

def build_inventory_img(item_images: list[PngImagePlugin.PngImageFile]) -> PngImagePlugin.PngImageFile:    
    ret_image = Image.new('RGB',(600, 200))
    x = 0
    y = 0
    count = 0

    for item in item_images:
        ret_image.paste(item, (x, y))
        x += 100
        count += 1
        if count > 5:
            y = 100
            x = 0
            count = 0
    return ret_image

def dc_image_file(data) -> PngImagePlugin.PngImageFile:
    file = build_inventory_img(get_inventory_images(data))
    return file

    # ret_image.save(f"{ITEM_IMG_PATH}inventory.png", "PNG")