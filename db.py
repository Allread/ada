import json
from crafter import Crafter
from generator import Generator
from item import Item
from recipe import Recipe

class DB:
    def __init__(self, path):
        # Parse data file
        with open(path) as f:
            data = json.load(f)

        # Parse items
        self.__items = {}
        self.__item_var_from_class_name = {}
        for item_data in data["items"].values():
            item = Item(item_data)
            self.__items[item.var()] = item
            self.__item_var_from_class_name[item_data["className"]] = item.var()

        # Parse crafters
        self.__crafters = {}
        self.__crafter_var_from_class_name = {}
        for building_data in data["buildings"].values():
            if "manufacturingSpeed" not in building_data["metadata"]:
                continue
            crafter = Crafter(building_data)
            self.__crafters[crafter.var()] = crafter
            self.__crafter_var_from_class_name[building_data["className"]] = crafter.var()

        # Parse generators
        self.__generators = {}
        for generator_data in data["generators"].values():
            # Replace the "Build_" prefix with the "Desc_" prefix to get the building class name.
            building_class_name = "Desc_" + generator_data["className"][6:]
            generator = Generator(data["buildings"][building_class_name], generator_data, self)
            self.__generators[generator.var()] = generator

        # Parse recipes
        # Create a dictionary from product => [recipe]
        self.__recipes_for_product = {}
        # Create a dictionary from ingredient => [recipe]
        self.__recipes_for_ingredient = {}
        self.__recipes = {}
        for recipe_data in data["recipes"].values():
            if not recipe_data["inMachine"]:
                continue
            recipe = Recipe(recipe_data, self)
            self.__recipes[recipe.var()] = recipe
            for ingredient in recipe_data["ingredients"]:
                ingredient_var = self.__item_var_from_class_name[ingredient["item"]]
                if ingredient_var not in self.__recipes_for_ingredient:
                    self.__recipes_for_ingredient[ingredient_var] = []
                self.__recipes_for_ingredient[ingredient_var].append(recipe)
            for product in recipe_data["products"]:
                product_var = self.__item_var_from_class_name[product["item"]]
                if product_var not in self.__recipes_for_product:
                    self.__recipes_for_product[product_var] = []
                self.__recipes_for_product[product_var].append(recipe)
                
        # Parse resources
        self.__resources = []
        for resource in data["resources"].values():
            self.__resources.append(self.__item_var_from_class_name[resource["item"]])


    def items(self):
        return self.__items

    def item_from_class_name(self, class_name):
        return self.items()[self.__item_var_from_class_name[class_name]]

    def recipes(self):
        return self.__recipes

    def recipes_for_product(self, product):
        if product not in self.__recipes_for_product:
            return []
        return self.__recipes_for_product[product]

    def recipes_for_ingredient(self, ingredient):
        if ingredient not in self.__recipes_for_ingredient:
            return []
        return self.__recipes_for_ingredient[ingredient]

    def resources(self):
        return self.__resources

    def crafters(self):
        return self.__crafters

    def crafter_from_class_name(self, class_name):
        return self.crafters()[self.__crafter_var_from_class_name[class_name]]

    def generators(self):
        return self.__generators