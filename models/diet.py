import json

class Diet:
    def __init__(self, username):
        self.username = username
        self.foods = []
        self.load_from_file()

    def add_food(self, food_info, quantity):
        """Adiciona informações de um alimento à dieta do usuário com base na quantidade."""
        food_info['username'] = self.username
        food_info['quantity'] = quantity  # Armazena a quantidade em gramas

        # Calcula os nutrientes com base na quantidade
        for nutrient in food_info['nutrients']:
            nutrient['total_value'] = (nutrient['value'] * quantity) / 100

        self.foods.append(food_info)
        self.save_to_file()

    def edit_food(self, fdc_id, new_quantity):
        """Edita a quantidade de um alimento na dieta do usuário."""
        for food in self.foods:
            if food['fdc_id'] == fdc_id:
                for nutrient in food['nutrients']:
                    nutrient['total_value'] = (nutrient['value'] * new_quantity) / 100
                food['quantity'] = new_quantity
                self.save_to_file()
                break

    def delete_food(self, fdc_id):
        """Remove um alimento da dieta do usuário."""
        self.foods = [food for food in self.foods if food['fdc_id'] != fdc_id]
        self.save_to_file()

    def save_to_file(self, filename='diet_data.json'):
        try:
            with open(filename, 'r') as file:
                all_data = json.load(file)
        except FileNotFoundError:
            all_data = []

        all_data = [food for food in all_data if food['username'] != self.username]
        all_data.extend(self.foods)

        with open(filename, 'w') as file:
            json.dump(all_data, file, indent=4)

    def load_from_file(self, filename='diet_data.json'):
        try:
            with open(filename, 'r') as file:
                all_data = json.load(file)
                self.foods = [food for food in all_data if food['username'] == self.username]
        except FileNotFoundError:
            self.foods = []
