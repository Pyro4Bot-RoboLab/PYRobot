#!/usr/bin/env python3
""" PYRO4BOT Generator launcher.
    This program generates the first directories and files that are needed to create your own pyro4bot robot.

Launcher file
"""
import os
import sys
import fileinput
import argparse
import json
import urllib.request
import shutil
from github import Github


def load_configuration(PYRO4BOT_HOME):
    """ It returns the configuration json file """
    try:
        with open(PYRO4BOT_HOME + '/configuration.json') as f:
            data = json.load(f)
            data["PYRO4BOT_HOME"] = PYRO4BOT_HOME
            if "PYRO4BOT_ROBOTS" in data:
                if data["PYRO4BOT_ROBOTS"][0] != "/":
                    data["PYRO4BOT_ROBOTS"] = os.path.join(data["PYRO4BOT_HOME"], data["PYRO4BOT_ROBOTS"])
        return data
    except:
        print("ERRORS in configuration file")
        sys.exit()


def get_PYRO4BOT_HOME():
    """ It turns back the environment path of the program Pyro4Bot """
    if "PYRO4BOT_HOME" not in os.environ:
        print("ERROR: PYRO4BOT_HOME not setted")
        print("please type export PYRO4BOT_HOME=<DIR> to set it up")
        sys.exit()
    else:
        return os.environ["PYRO4BOT_HOME"]


PYRO4BOT_HOME = get_PYRO4BOT_HOME()
configuration = load_configuration(PYRO4BOT_HOME)
configuration["generator"] = os.path.join(PYRO4BOT_HOME, "generator")
sys.path.append(PYRO4BOT_HOME)
from node.libs.myjson import MyJson


def check_args(args=None):
    """ It checks the arguments passed to the main program and returns them in a dictionary  """
    parser = argparse.ArgumentParser(description='Generating or update a robot')
    parser.add_argument('robot',
                        help="Name for a Robot",
                        type=str)
    parser.add_argument('-p', '--path',
                        help='path to create robot',
                        default=configuration["PYRO4BOT_ROBOTS"],
                        type=str)
    parser.add_argument('-u', '--update',
                        required=False,
                        nargs="?",
                        help='update not implemented components from the repository',
                        default=False)
    parser.add_argument('-j', '-J', '--json',
                        help='json file to create robot (optional)')

    results = vars(parser.parse_args(args))

    results['path'] = os.path.abspath(results['path'])
    results['update'] = True if results['update'] is None else False
    if results['json'] is None:
        results['json'] = os.path.join(results["path"], results["robot"], "model", results['robot'] + '.json')
    elif '.json' not in results['json']:
        results['json'] = os.path.abspath(results['json'] + '.json')
    else:
        results['json'] = os.path.abspath(results['json'])

    return results


def substitute_params(file, words):
    """ It substitutes one or several words in the file passed by parameter.
    This is used to change a template file with key words to the actual current word needed in each case """
    for line in fileinput.input([file], inplace=True):
        for old, new in words:
            line = line.replace(old, new)
        print(line, end='')


def extract_element(conf):
    """ It inspects the bot's json file searching for the components and services of the robot """
    json = MyJson(filename=conf['json']).json

    json_services_classes = []
    json_components_classes = []

    for (key, value) in json['services'].items():
        json_services_classes.append(value['cls'])
    for (key, value) in json['components'].items():
        json_components_classes.append(value['cls'])

    return json_services_classes, json_components_classes


def __search_in__(collection, element):
    """ It searches an element or a piece of an element in a collection and returns the whole element back
    This is used to searches the name of a component or a service in a collection of string paths """
    for item in collection:
        if element in item:
            return item
    return None


def __search_local__(current_dir, filename):
    """ It searches and return the path to the missing file if it is the directory passed by parameter """
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if filename in file:
                path_file = os.path.join(root, file)
                return path_file
    return None


# TODO: this only searches in one repository; it doesn't check if there are more than one repository in the config file
def find_element(module, json_module_classes, repository, bot_name):
    """ It searches the element (component of service) in the repository of Pyro4Bot and return the url path """
    stable = repository.get_contents(path=module + '/stable')
    developing = repository.get_contents(path=module + '/developing')
    stable = [element.path for element in stable]
    developing = [element.path for element in developing]

    routes = []
    for element in json_module_classes:
        current_dir = os.path.join(configuration['PYRO4BOT_ROBOTS'], bot_name)

        obj = __search_local__(current_dir, element)
        if obj is not None:
            continue
        else:
            obj = __search_in__(stable, element)
        obj = obj if obj is not None else __search_in__(developing, element)
        routes.append(obj) if obj is not None else print("ERROR with the element: ", element,
                                                         ",\t it's not found in the repository. \nYou should define in "
                                                         "the directories of your robot")

    return routes


def download_element(bot_name, url_directory):
    """ It downloads the file of the component or service from the GitHub repository of Pyro4Bot """
    global configuration
    local_path = os.path.join(configuration['PYRO4BOT_ROBOTS'], bot_name)
    for each in url_directory:
        directory = each.replace('stable/', '')
        directory = directory.replace('developing/', '')
        directory = os.path.join(local_path, *directory.split('/'))
        if not os.path.exists(directory):
            os.makedirs(directory)
            # Generate an init file to each python package (each directory)
            with open(os.path.join(directory, '__init__.py'), 'a+') as f:
                f.write('\n')
        for element_name in each.split('/'):  # Only takes the string of the element (component of service)
            if element_name not in ('components', 'services', 'stable', 'developing'):
                file = os.path.join(directory, element_name + '.py')
                file_url = configuration['REPOSITORIES'][0] + each + '/' + element_name + '.py'
                urllib.request.urlretrieve(file_url, file)


def update_robot(conf):
    """ It checks and updates the directories and files needed to run the robot.
    this only can be used once the user has described its robot in the json file.

    If the services and components of the robots are already in the repository, they will be downloaded.
    If not, the user must have developed the necessary files to handle those dependencies of the robots.
    If neither of them are completed, this will show an error message to the user. """
    json_services_classes, json_components_classes = extract_element(conf)

    # #  github = Github(login_or_token="17143d9e9f8b00012627e2545eefce8fda07d216")
    repository = Github("pyro4bot", "90racano").get_user().get_orgs()[0].get_repo('Components')

    url_services = find_element(module='services', json_module_classes=json_services_classes, repository=repository,
                                bot_name=conf['robot'])
    url_components = find_element(module='components', json_module_classes=json_components_classes,
                                  repository=repository, bot_name=conf['robot'])

    download_element(conf['robot'], url_services)
    download_element(conf['robot'], url_components)


def create_robot(conf):
    """ The first execution of this program will create the structure, files and directories needed to a
    pyro4bot robot """
    global configuration
    robot_path = os.path.join(conf["path"], conf["robot"])
    try:
        if not os.path.exists(conf["path"]):
            os.makedirs(conf["path"])
        if not os.path.exists(robot_path):
            # Whole structure of robot folders
            source = os.path.join(configuration['generator'], 'template_robot')
            shutil.copytree(source, robot_path)

            # Json file
            source = os.path.join(robot_path, "model", "_robot.json")
            if conf['json'] is not None:
                conf['json'] = conf['json'] + '.json' if '.json' not in conf['json'] else conf['json']
                target = os.path.join(robot_path, 'model', conf['json'])
            else:
                target = os.path.join(robot_path, 'model', conf['robot'] + '.json')
            shutil.move(source, target)
            substitute_params(file=target,
                              words=[('<robot>', conf['robot']), ('<ethernet>', configuration['ETHERNET'])])

            # Python Client file
            source = os.path.join(robot_path, 'clients', 'template_client.py')
            target = os.path.join(robot_path, 'clients', 'client_' + conf['robot'] + '.py')
            shutil.move(source, target)
            substitute_params(file=target,
                              words=[('<robot>', conf['robot']), ('<ethernet>', configuration['ETHERNET'])])

            target = os.path.join(configuration['PYRO4BOT_ROBOTS'], conf['robot'], 'start.py')
            substitute_params(file=target,
                              words=[('<robot>', conf['robot']), ('<ethernet>', configuration['ETHERNET'])])

            return True
        else:
            print("The robot {} exists".format(conf["robot"]))
            return True
    except:
        print("ERROR: There has been an error with the files and folders of your robot")
        return False


if __name__ == "__main__":
    """ Main function of this program.
    It checks the argument passed to the program and generate the necessary files to each case,
    depending on the current development of the robot.

    The first time it is executed, it should be using only the argument 'robot_name' with the name of the robot;
    for example: python3 generate_robot.py robot_name or ./generate_robot.py robot_name

    The second time, it expects the user has already described the robot in the json file, and developed the
    components and services needed in case they are not in the repository. Then, the execution should update the
    directories like this: python3 generate_robot.py robot_name --update
    
    It shows the different available commands using --help (-h) argument also. (f.e.: ./generate_robot.py --help) """

    args = check_args(sys.argv[1:])

    if create_robot(args):
        if args['update']:
            update_robot(args)
    else:
        if args['update']:
            print("You cannot update the robot because it still doesn't exist.")
