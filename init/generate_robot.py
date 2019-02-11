#!/usr/bin/env python3
""" PYRO4BOT Generator launcher.
    This program generates the first directories and files that are needed to create your own pyro4bot robot.

Launcher file
"""
import os
import sys
import fileinput
import urllib.request
from github import Github

sys.path.append('../developing')

__base_url__ = 'https://raw.githubusercontent.com/Pyro4Bot-RoboLab/Components/developing/'
__json_bot_filepath__ = ""


# TODO : make it more abstract => defaul template // specific element template
def __create_template__(url_module, local_path):
    """ It creates the templates for the components that must be develop """
    file = os.path.join(local_path, 'Template.py')
    file_url = __base_url__ + url_module + '/Template.py'
    urllib.request.urlretrieve(file_url, file)


def __create_json__(path, bot_name):
    """ It creates the json file for the robot from a template """
    __json_bot_file__ = os.path.join(path, bot_name + '.json')
    json_url = __base_url__ + 'init/bot_template.json'
    urllib.request.urlretrieve(json_url, __json_bot_file__)
    try:
        for line in fileinput.input([__json_bot_file__], inplace=True):
            print(line.replace('botname', bot_name), end='')
    except IOError:
        print("There has been an error with the template con the bot")
        raise


def __extract_element__(bot_name):
    """ It inspects the bot's json file searching for the components and services of the robot """
    from node.libs.myjson import MyJson

    _path_ = os.path.join('robots', bot_name)
    __json_bot_file__ = os.path.join(_path_, bot_name + '.json')
    json = MyJson(filename=__json_bot_file__).json

    json_services_classes = []
    json_components_classes = []

    for (key, value) in json['services'].items():
        json_services_classes.append(value['cls'])
    for (key, value) in json['components'].items():
        json_components_classes.append(value['cls'])

    return json_services_classes, json_components_classes


# TODO : More efficient!!
def __find_element__(module, json_module_classes, repository):
    """ It searches the element (component of service) in the repository of Pyro4Bot and return the url path """
    stable = repository.get_contents(path=module + '/stable')
    developing = repository.get_contents(path=module + '/developing')
    routes = []
    for element in stable:
        routes.append(element.path)
    stable = routes
    routes = []
    for element in developing:
        routes.append(element.path)
    developing = routes

    routes = []
    flag = False
    for element in json_module_classes:
        for remote in stable:
            if element in remote:
                routes.append(remote)
                flag = True
        if not flag:
            for remote in developing:
                routes.append(remote)
                flag = True
        flag = False

    return routes


def __download_element__(bot_name, url_directory):
    """ It downloads the directory of the component or service from the repository of GitHub """
    local_path = os.path.join('robots', bot_name)
    element_name = []
    url_element = []
    for each in url_directory:
        aux = each.split('/')
        aux = os.path.join(*aux)
        file = os.path.join(local_path, aux)
        if not os.path.exists(file):
            os.makedirs(file)
        for string in each.split('/'):
            if string not in ('components', 'services', 'stable', 'developing'):
                element_name.append(string)
                url_element.append(each + '/' + string + '.py')

    for element in url_element:
        element_name = element.split('/')
        element_name = os.path.join(*element_name)
        file = os.path.join(local_path, element_name)
        file_url = __base_url__ + element
        urllib.request.urlretrieve(file_url, file)


def __download_start__(bot_name):
    # TODO: Download start_node.py as start.py
    url = 'https://raw.githubusercontent.com/Pyro4Bot-RoboLab/Pyro4Bot/developing/developing/start_pyro4bot.py'
    file = os.path.join('robots', bot_name)
    file = os.path.join(file, 'start.py')
    urllib.request.urlretrieve(url, file)


def __update_robot__(bot_name):
    """ It checks and updates the directories and files needed to run the robot.
    this only can be used once the user has described its robot in the json file.

    If the services and components of the robots are already in the repository, they will be downloaded.
    If not, the user must have developed the necessary files to handle those dependencies of the robots.
    If neither of them are completed, this will show an error message to the user.
    """
    json_services_classes, json_components_classes = __extract_element__(bot_name)

    #  github = Github(login_or_token="17143d9e9f8b00012627e2545eefce8fda07d216")
    github = Github("pyro4bot", "90racano")

    repository = github.get_user().get_orgs()[0].get_repo('Components')
    url_services = __find_element__(module='services', json_module_classes=json_services_classes, repository=repository)
    url_components = __find_element__(module='components', json_module_classes=json_components_classes,
                                      repository=repository)
    __download_element__(bot_name, url_services)
    __download_element__(bot_name, url_components)

    __download_start__(bot_name)


def __create_robot__(bot_name):
    """ The first execution of this program will create the structure, files and directories needed to a
    pyro4bot robot
    """
    path = os.path.join('robots', bot_name)
    if not os.path.exists(path):
        os.makedirs(path)
    for module in ['services', 'components']:
        if not os.path.exists(os.path.join(path, module)):
            os.makedirs(os.path.join(path, module))
            __create_template__(module, os.path.join(path, module))
    __create_json__(path, bot_name)


if __name__ == "__main__":
    """ Main function of this program.
    It checks the argument passed to the program and generate the necessary files to each case,
    depending on the current development of the robot.

    The first time it is executed, it should be using only the argument 'robot_name' with the name of the robot;
    for example: python3 generate_robot.py robot_name

    The second time, it expects the user has already described the robot in the json file, and developed the 
    components and services needed in case they are not in the repository. Then, the execution should update the 
    directories like this: python3 generate_robot.py -update
    """
    try:
        if len(sys.argv) < 2:
            print("File was expected as argument.")
            os._exit(0)
        elif len(sys.argv) == 3:
            argument = sys.argv[1]
            if argument == '-update':
                argument = sys.argv[2]
                argument.replace('.json', '')  # just having the precaution of not misspelling the name
                __update_robot__(argument)
                print("ROBOT READY TO RUN")
        else:
            argument = sys.argv[1]
            if argument == '-update':
                print("File was expected as argument.")
                os._exit(0)
            else:
                argument.replace('.json', '')  # just having the precaution of not misspelling the name
                __create_robot__(argument)
                print("BASE ROBOT CREATED")
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
    except Exception:
        raise
