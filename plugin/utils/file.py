import yaml
import json
import chevron
from yaml.loader import SafeLoader
from plugin import plugin_path
import os
import sys
import subprocess
import zipfile


class ZipUtilities:
    """
    TO DO
    """

    base_path: str

    def add_to_zip(self, path, filename):
        self.base_path = f"{get_current_pwd()}/{path}"
        with zipfile.ZipFile(filename, 'a') as zip_file:
            if os.path.isfile(path):
                zip_file.write(path, path)
            else:
                os.chdir(self.base_path)
                self.add_folder_to_zip(zip_file, '.')
            zip_file.close()

    def add_folder_to_zip(self, zip_file, folder):
        for file in os.listdir(folder):

            full_path = os.path.join(folder, file)

            if os.path.isfile(full_path):
                print(f"File added: {full_path}")
                zip_file.write(full_path)
            elif os.path.isdir(full_path):
                print(f"Entering folder: {full_path}")
                self.add_folder_to_zip(zip_file, full_path)


def get_current_pwd():
    return os.getcwd()


def create_lambda_package(folder: str, output_zip: str):

    out_dir = get_current_pwd()

    remove_from_os(f"{out_dir}/{folder}/{output_zip}")
    utilities = ZipUtilities()
    utilities.add_to_zip(folder, f"{out_dir}/{folder}/{output_zip}")
    os.chdir(out_dir)


def remove_from_os(path: str):
    if os.path.exists(path):
        subprocess.call(f'rm -rf {path}', shell=True)


def read_yaml(path: str):
    try:
        with open(path, encoding="utf-8") as yml:
            return yaml.load(yml, Loader=SafeLoader)
    except FileNotFoundError as error:
        print(error)
        sys.exit(0)


def read_plugin_yaml(path: str):
    try:
        full_path = os.path.abspath(os.path.join(plugin_path, f"{path}"))
        with open(full_path, encoding="utf-8") as yml:
            return yaml.load(yml, Loader=SafeLoader)
    except FileNotFoundError as error:
        print(error)
        sys.exit(0)


def get_full_path(path):
    return os.path.abspath(os.path.join(plugin_path, f"{path}"))


def read_json(path: str):
    try:
        full_path = os.path.abspath(os.path.join(plugin_path, f"{path}"))
        with open(full_path, encoding="utf-8") as json_file:
            return json.load(json_file)
    except FileNotFoundError as err:
        print(err)
        sys.exit(0)


def interpolate_json_template(template, data: dict):
    try:
        res = chevron.render(json.dumps(template), data)
        return json.loads(res)
    except FileNotFoundError as err:
        print(err)
        sys.exit(0)
