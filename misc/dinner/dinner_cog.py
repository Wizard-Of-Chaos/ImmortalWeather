import json
import re

import discord as dc
from discord.ext import commands
from discord import app_commands
import user_reg as urg
import random
import os

TITLE_REGEX:str = "(.*)(?=\\|Ingredients)"
INGREDIENT_REGEX:str = "(?<=Ingredients\\|)(.*)(?=\\|Equipment)"
EQUIPMENT_REGEX:str = "(?<=Equipment\\|)(.*)(?=\\|Method)"
METHOD_REGEX:str = "(?<=Method\\|)(.*)"

JSON_REQUIRED_KEYS_ENTREE:list[str] = [
    'name',
    'cook_time',
    'ingredients',
    'equipment',
    'method',
    'notes'
]

JSON_REQUIRED_KEYS_DRINK:list[str] = [
    'name',
    'ingredients',
    'method',
    'notes'
]

class DinnerCog(commands.Cog):
    def __init__(self, bot, dinner_filename:str):
        print("Initializing foodie cog...")
        self.bot = bot
        self.fname = dinner_filename
        self.load(dinner_filename)

    def load(self, loadfile):
        with open(loadfile, 'r') as file:
            self.dinnerfile = json.load(file)
        self.entrees = []
        for entree in self.dinnerfile['entrees']:
            self.entrees.append(entree)
        self.sides = []
        for side in self.dinnerfile['sides']:
            self.sides.append(side)
        self.drinks = []
        for drink in self.dinnerfile['drinks']:
            self.drinks.append(drink)
        #self.save()

    def save(self):
        dumper: dict = {} #MASSIVE FUCKING DUMPER HERE
        dumper['entrees'] = self.entrees
        dumper['sides'] = self.sides
        dumper['drinks'] = self.drinks
        with open(self.fname, "+w") as savefile:
            json.dump(dumper, savefile, indent=4)

    def discord_formatted_entree(self, recipe:dict) -> str:
        msg = '# '
        msg += recipe['name'] + "\n"

        if 'cook_time' in recipe:
            msg += '### Cook Time: ' + recipe['cook_time'] + "\n"

        msg += '## Ingredients\n'
        for ingredient in recipe['ingredients']:
            msg += '* ' + ingredient + '\n'

        if 'equipment' in recipe:
            msg += '## Equipment\n'
            for equip in recipe['equipment']:
                msg += '* ' + equip + '\n'

        msg += '## Method\n'
        for line in recipe['method']:
            msg += '* ' + line + '\n'

        if len(recipe['notes']) != 0:
            msg += "### Notes\n"
            for line in recipe['notes']:
                msg += '* ' + line + '\n'
        return msg
    
    def get_choice_from_list(self, foodlist:list, searchparams:str = None) -> str | None:
        if searchparams == None:
            return self.discord_formatted_entree(random.choice(foodlist))
        
        params: list[str] = searchparams.split()
        possible_food: list = []

        for recipe in foodlist:
            ingredients = ''.join([i for i in recipe['ingredients']])

            valid:bool = True 
            for param in params:
                if param not in ingredients:
                    valid=False
                    break

            if not valid:
                continue

            possible_food.append(recipe)
        
        if len(possible_food) == 0:
            return None
        
        return self.discord_formatted_entree(random.choice(possible_food))
    
    @app_commands.command(name="dinner", description="Get a random entree!")
    @app_commands.describe(searchparams="Args for dinner.")
    async def entree(self, interaction: dc.Interaction, searchparams:str = None):
        choice = self.get_choice_from_list(self.entrees, searchparams)
        if choice == None:
            await interaction.response.send_message("Nothing matched your search parameters, you *picky eating* motherfucker.")
            return
        await interaction.response.send_message(choice)

    @app_commands.command(name="side", description="Get a random side dish!")
    async def side(self, interaction: dc.Interaction, searchparams:str = None):
        choice = self.get_choice_from_list(self.sides, searchparams)
        if choice == None:
            await interaction.response.send_message("Nothing matched your search parameters, you *picky eating* motherfucker. Just eat a goddamn vegetable!")
            return
        await interaction.response.send_message(choice)

    @app_commands.command(name="drink", description="Get a random drink!")
    async def drink(self, interaction: dc.Interaction, searchparams:str = None):
        choice = self.get_choice_from_list(self.drinks, searchparams)
        if choice == None:
            await interaction.response.send_message("Nothing matched your search parameters, you *picky drinking* motherfucker.")
            return
        await interaction.response.send_message(choice)

    @app_commands.command(name="universal_spice", description="In case you forgot.")
    async def universal_spice(self, interaction: dc.Interaction):
        await interaction.response.send_message("The 'Universal Spice' refers to either [Montreal Steak Seasoning](<https://www.mccormick.com/products/mccormick-grill-mates-montreal-steak-seasoning-3-4-oz>) OR\n3 tbsp the aforementioned seasoning\n1 tsp garlic powder\n1/2 tsp chili powder\n1/2 tsp oregano\n1/2 tsp thyme")

    @app_commands.command(name="template_submission", description="Gets the JSON template for submitting a recipe.")
    async def templatesub(self, interaction: dc.Interaction):
        await interaction.response.send_message(
            """
Submit entrees, sides, and drinks as JSON files and they'll be added to the list.
Each line should be its own string in the arrays.

Entree / side template:
```json
{
    "name": "",
    "cook_time": "",
    "ingredients": [
    ],
    "equipment": [
    ],
    "method": [
    ],
    "notes": [
    ]
}```
Drink template:
```json
{
    "name": "",
    "ingredients": [
    ],
    "method": [
    ],
    "notes": [
    ]
}```
            """
        )

    async def add_recipe(self, interaction: dc.Interaction, which:str, file: dc.Attachment):
        if file.content_type != "application/json; charset=utf-8":
            await interaction.response.send_message("That's not the right file type. Must be JSON in UTF-8.")
            return
        fname:str = f"misc/storage/tmp_{file.filename}"
        await file.save(fname)
        loaded_json: dict = {}
        with open(fname, "r+") as tmp:
            loaded_json = json.load(tmp)

        os.remove(fname)
        required_strings: list[str] = JSON_REQUIRED_KEYS_ENTREE
        if which == 'drink':
            required_strings = JSON_REQUIRED_KEYS_DRINK

        for key in required_strings:
            if key not in loaded_json.keys():
                await interaction.response.send_message("JSON is missing required keys. Not added.")
                return
            if key == 'name' or key == 'cook_time':
                if type(loaded_json[key]) != str:
                    await interaction.response.send_message("Type on key or cook time is malformed. Not added.")
                    return 
            else:
                if type(loaded_json[key]) != list:
                    await interaction.response.send_message("One of the string lists is malformed. Not added.")
                    return
        
        foodlist:list = self.entrees
        if which == 'side':
            foodlist = self.sides
        elif which == 'drink':
            foodlist = self.drinks

        for recipe in foodlist:
            if loaded_json['name'] == recipe['name']:
                await interaction.response.send_message(f"We already have that {which}!")
                return

        if which == 'entree':
            self.entrees.append(loaded_json)
        elif which == 'side':
            self.sides.append(loaded_json)
        elif which == 'drink':
            self.drinks.append(loaded_json)
        
        self.save()
        await interaction.response.send_message(f"Added submission to the list!\n{self.discord_formatted_entree(loaded_json)}")

    @app_commands.command(name="submit_entree", description="Submit a JSON file for an entree.")
    async def submit_entree(self, interaction: dc.Interaction, file: dc.Attachment):
        await self.add_recipe(interaction, 'entree', file)

    @app_commands.command(name="submit_side", description="Submit a JSON file for a side dish.")
    async def submit_side(self, interaction: dc.Interaction, file: dc.Attachment):
        await self.add_recipe(interaction, 'side', file)

    @app_commands.command(name="submit_drink", description="Submit a JSON file for a mixed drink.")
    async def submit_drink(self, interaction: dc.Interaction, file: dc.Attachment):
        await self.add_recipe(interaction, 'drink', file)

    # turns a discord message into the accepted format for the json dinner setup. unused atm
    def convert_discord_dinner_str(self, msg: dc.Message) -> str:
        content: str = msg.content
        content.replace("\r", "")
        content.replace("\n", "|")
        return content

    # Assumes that the thing in question is a bunch of |-separated strings. unused atm.
    def build_json_dinner_object(self, dinnerstr:str):
        dinnerstr.rstrip()
        dinnerstr = dinnerstr.replace('### ', '')
        dinnerstr = dinnerstr.replace('## ', '')
        dinnerstr = dinnerstr.replace('# ', '')
        dinnerstr = dinnerstr.replace('* ', '')
        dinnerstr = dinnerstr.replace('- ', '')
        with open('fixed_format.txt', "w+") as file:
            file.write(dinnerstr)

        recipe: dict = {}

        title_result = re.search(TITLE_REGEX, dinnerstr)
        if title_result:
            recipe['name'] = title_result.group()

        recipe['cook_time'] = ''

        ingredient_result = re.search(INGREDIENT_REGEX, dinnerstr)
        if ingredient_result:
            splits = re.split("\\|", ingredient_result.group())
            recipe['ingredients'] = splits

        equipment_result = re.search(EQUIPMENT_REGEX, dinnerstr)
        if equipment_result:
            splits = re.split("\\|", equipment_result.group())
            recipe['equipment'] = splits

        method_result = re.search(METHOD_REGEX, dinnerstr)
        if method_result:
            splits = re.split("\\|", method_result.group())
            recipe['method'] = splits

        recipe['notes'] = []
        return recipe