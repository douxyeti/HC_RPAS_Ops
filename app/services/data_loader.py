import json

class DataLoader:
    @staticmethod
    def load_from_config(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def map_to_model(data, model_class):
        return [model_class(**item) for item in data]
