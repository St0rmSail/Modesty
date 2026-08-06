import yaml

def load_config(filename="Brain/modesty.yaml"):
    with open(filename, "r") as file:
        return yaml.safe_load(file)