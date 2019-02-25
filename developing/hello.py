import os
import urllib.request
import json


def __get_source_list():
    """ It downloads the source list from the repository of Pyro4Bot, then delete it and return a dict with the info """
    file = os.path.join(os.getcwd(), 'source-list.json')
    file_url = 'https://raw.githubusercontent.com/Pyro4Bot-RoboLab/Components/developing/source-list.json'
    urllib.request.urlretrieve(file_url, file)
    with open(file) as f:
        data = json.load(f)
    os.remove(file)
    return data


