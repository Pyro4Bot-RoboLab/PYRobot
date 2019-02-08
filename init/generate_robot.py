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

__url__ = 'https://raw.githubusercontent.com/Pyro4Bot-RoboLab/Components/developing/'
__json_bot_file__ = ""


# TODO : make it more abstract => defaul template // specific element template
def __create_template__(url_module, local_path):
    """ It creates the templates for the components that must be develop """
    file = os.path.join(local_path, 'Template.py')
    file_url = __url__ + url_module + '/Template.py'
    urllib.request.urlretrieve(file_url, file)


def __create_json__(path, bot_name):
    """ It creates the json file for the robot from a template """
    __json_bot_file__ = os.path.join(path, bot_name + '.json')
    json_url = __url__ + 'init/bot_template.json'
    urllib.request.urlretrieve(json_url, __json_bot_file__)
    try:
        for line in fileinput.input([__json_bot_file__], inplace=True):
            print(line.replace('botname', bot_name), end='')
    except IOError:
        print("There has been an error with the template con the bot")
        raise


def __extract_element__():
    pass


def __find_element__():
    pass


def __download_directory__():
    pass


def __update_robot__(bot_name):
    """ It checks and updates the directories and files needed to run the robot.
    this only can be used once the user has described its robot in the json file.

    If the services and components of the robots are already in the repository, they will be downloaded.
    If not, the user must have developed the necessary files to handle those dependencies of the robots.
    If neither of them are completed, this will show an error message to the user.
    """
    sys.path.append('../developing')
    from node.libs.myjson import MyJson

    #  github = Github(login_or_token="17143d9e9f8b00012627e2545eefce8fda07d216")
    #    print(github.get_project(id=0))
    #   github = Github(base_url='https://github.com/Pyro4Bot-RoboLab/Components',
    #                   login_or_token='17143d9e9f8b00012627e2545eefce8fda07d216')

    github = Github("pyro4bot", "90racano")

    org = github.get_user().get_orgs()[0]
    print(org)
    repository = org.get_repo('Components')
    print(repository)
    stable = repository.get_contents(path='components/stable')
    developing = repository.get_contents(path='components/developing')
    for com in stable:
        print(com)
        print(com.path)
        print(type(com))

    # sha = get_sha_for_tag(repository, 'infrared')
    # print(sha)

    #   download_directory(repository=repository, server_path='stable/infrared')

    _path_ = os.path.join('robots', bot_name)
    __json_bot_file__ = os.path.join(_path_, bot_name + '.json')
    json = MyJson(filename=__json_bot_file__).json

    services_classes = []
    components_classes = []

    for (key, value) in json['services'].items():
        class_name = value['cls']
        services_classes.append(class_name)
        #    if class_name in [com.path for com in stable]:
        #       urllib.request.urlretrieve(com.path)
        file_url = __url__ + 'services/'  # TODO: not completed
        file = _path_ + 'services/' + class_name + '.py'
    #    urllib.request.urlretrieve(file_url, file)  # TODO: not completed

    print("services classes")
    print(services_classes)

    for (key, value) in json['components'].items():
        components_classes.append(value['cls'])

    print(services_classes)
    print(components_classes)


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
        else:
            argument = sys.argv[1]
            if argument == '-update':
                print("File was expected as argument.")
                os._exit(0)
            else:
                argument.replace('.json', '')  # just having the precaution of not misspelling the name
                __create_robot__(argument)
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
    except Exception:
        raise
