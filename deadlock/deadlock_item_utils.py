import requests
from PIL import Image, PngImagePlugin
import os
import io
import json
import random

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

def valid_random_item(id: int) -> bool:
    item = __ITEMS__[id]
    # print(item["name"])
    if 'disabled' in item:
        if item['disabled'] == True:
            return False
    if not item["shopable"]:
        return False
    if item["cost"] < 3200:
        return False
    return True

def randomized_inventory() -> list[int]:
    inventory = []
    while len(inventory) < 12:
        item = random.choice(list(__ITEMS__.keys()))
        #needs to be purchaseable, 3200+ souls, not disabled and not already in inventory
        while item in inventory or valid_random_item(item) == False:
            item = random.choice(list(__ITEMS__.keys()))
        inventory.append(item)
        # print(__ITEMS__[item]["name"])
    return inventory

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

def get_inventory_images_from_ids(data: list[int]) -> list[PngImagePlugin.PngImageFile]:
    ret = []
    for x in data:
        ret.append(get_item_img(x))
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

def randomized_inv_image() -> PngImagePlugin.PngImageFile:
    file = build_inventory_img(get_inventory_images_from_ids(randomized_inventory()))
    return file
    # ret_image.save(f"{ITEM_IMG_PATH}inventory.png", "PNG")