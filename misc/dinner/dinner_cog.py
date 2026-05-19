import json
import re

import discord as dc
from discord.ext import commands
from discord import app_commands
import requests
import user_reg as urg
import datetime
import random

TITLE_REGEX = "(.*)(?=\\|Ingredients)"
INGREDIENT_REGEX = "(?<=Ingredients\\|)(.*)(?=\\|Equipment)"
EQUIPMENT_REGEX = "(?<=Equipment\\|)(.*)(?=\\|Method)"
METHOD_REGEX = "(?<=Method\\|)(.*)"

class DinnerCog(commands.Cog):
    def __init__(self, bot, file:str):
        print("Initializing foodie cog...")
        self.bot = bot
        self.load(file)

    def load(self, file):
        with open(file, 'r') as file:
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

    def save(self):
        pass

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
    
    @app_commands.command(name="dinner", description="Get a random entree!")
    async def entree(self, interaction: dc.Interaction):
        await interaction.response.send_message(self.discord_formatted_entree(random.choice(self.entrees)))

    @app_commands.command(name="side", description="Get a random side dish!")
    async def side(self, interaction: dc.Interaction):
        await interaction.response.send_message(self.discord_formatted_entree(random.choice(self.sides)))

    @app_commands.command(name="drink", description="Get a random drink!")
    async def drink(self, interaction: dc.Interaction):
        await interaction.response.send_message(self.discord_formatted_entree(random.choice(self.drinks)))

    @app_commands.command(name="universal_spice", description="In case you forgot.")
    async def universal_spice(interaction: dc.Interaction):
        await interaction.response.send_message("The 'Universal Spice' refers to either [Montreal Steak Seasoning](<https://www.mccormick.com/products/mccormick-grill-mates-montreal-steak-seasoning-3-4-oz>!!) OR\n3 tbsp the aforementioned seasoning\n1 tsp garlic powder\n1/2 tsp chili powder\n1/2 tsp oregano\n1/2 tsp thyme")

    # Assumes that the thing in question is a bunch of |-separated strings
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