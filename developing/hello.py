import os
import urllib.request
import json

path = "robots/paco"
path = os.path.abspath(os.path.join(*path.split("/")))

print(os.path.abspath(path))

local = [item for l in [[os.path.join(root, file) for file in files] for root, dirs, files in os.walk(path)] for item in
         l]
print(local)

__search_in__ = lambda collection, element: next(
    (item for item in collection if element.lower() == item.split('/')[-1].lower()), None)

print("Printing 'local'")
print(*local, sep="\n")
print("\n\n")

print("searh element : pantilt.py")
print(__search_in__(local, "pantilt.py"))
print("searh element : infrared.py")
print(__search_in__(local, "infrared.py"))
print("searh element : usbcam")
print(__search_in__(local, "usbcam"))


def __get_source_list():
    file = os.path.join(os.getcwd(), 'source-list.json')
    file_url = 'https://raw.githubusercontent.com/Pyro4Bot-RoboLab/Components/developing/source-list.json'
    urllib.request.urlretrieve(file_url, file)

    with open(file) as f:
        data = json.load(f)

    os.remove(file)
    return data


print("\n\n\t Get source list: ")

source_list = __get_source_list()


json_component_classes = ['pantilt', 'basemotion', 'laser', 'l298n']
json_services_classes = ['usbserial', 'gpioservice', 'picam']

modules = ('services', 'components')

components = source_list['components']
services = source_list['services']

print(services)
print(type(services))

print("service picam_socket: -->  ", services['picam_socket'])
# print("print picam_soket . key(): --> ", services['picam_socket'].key())

# print(" print services[i] --> ", services[0])

element = 'pantilt'

stable = []
for key, value in components.items():
    print(key)
    print(value)

stable = [val for key, val in components.items() if val['stable']]

for item in stable:
    if element in local:
        item['local'] = path
    else:
        item['local'] = False

print("lsldlfsakñdfskajfs")
print(stable)


print("element: \n", element)
print("STABLE: \n", stable)

for key, item in components:
    if element in local:
        item['local'] = path
    else:
        item['local'] = False

stable = [(key, val['content'], val['path']) for key, val in components.items() if val['local'] and (
          element == key or element == val['content'])]

print("element: \n", element)
print("STABLE: \n", stable)
