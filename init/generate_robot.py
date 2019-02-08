#!/usr/bin/env python3
""" PYRO4BOT Generator launcher.
    This program generates the first directories and files that are needed to create your own pyro4bot robot.

Launcher file
"""
import os
import sys
import fileinput
import urllib.request

__url__ = 'https://raw.githubusercontent.com/Pyro4Bot-RoboLab/Components/developing/'
__json_bot_file__ = ""


def get_sha_for_tag(repository, tag):
    """
    Returns a commit PyGithub object for the specified repository and tag.
    """
    branches = repository.get_branches()
    matched_branches = [match for match in branches if match.name == tag]
    if matched_branches:
        return matched_branches[0].commit.sha

    tags = repository.get_tags()
    matched_tags = [match for match in tags if match.name == tag]
    if not matched_tags:
        raise ValueError('No Tag or Branch exists with that name')
    return matched_tags[0].commit.sha


def download_directory(repository, sha, server_path):
    """
    Download all contents at server_path with commit tag sha in
    the repository.
    """
    contents = repository.get_dir_contents(server_path, ref=sha)

    for content in contents:
        print("Processing ", content.path)
        if content.type == 'dir':
            download_directory(repository, sha, content.path)
        else:
            try:
                path = content.path
                file_content = repository.get_contents(path, ref=sha)
                file_data = base64.b64decode(file_content.content)
                file_out = open(content.name, "w")
                file_out.write(file_data)
                file_out.close()
            except (GithubException, IOError) as exc:
                logging.error('Error processing %s: %s', content.path, exc)


def update_robot(bot_name):
    """ It checks and updates the directories and files needed to run the robot.
    this only can be used once the user has described its robot in the json file.

    If the services and components of the robots are already in the repository, they will be downloaded.
    If not, the user must have developed the necessary files to handle those dependencies of the robots.
    If neither of them are completed, this will show an error message to the user.
    """
    sys.path.append('../developing')
    from node.libs.myjson import MyJson
    from github import Github

    github = Github(login_or_token="17143d9e9f8b00012627e2545eefce8fda07d216")
    print(github.get_project('pyro4bot'))
    #   github = Github(base_url='https://github.com/BertoSerrano/pyro4bot_components',
    #                   login_or_token='17143d9e9f8b00012627e2545eefce8fda07d216')

    variable = github.get_user()
    print(variable)
    variable = variable.get_repos()
    print(variable)
    for repo in github.get_user().get_repos():
        print(repo.name)

    # org = github.get_organization('BertoSerrano')
    # repo = github.get_repos("BertoSerrano/pyro4bot_components")
    # contents = repo.get_page("README.md")
    # print("using pygithub library! \n")
    # print(contents)

    # repository_name = 'pyro4bot_components'
    # repository = organization.get_repo(repository_name)
    # sha = get_sha_for_tag(repository, )

    _path_ = os.path.join('robots', bot_name)
    __json_bot_file__ = os.path.join(_path_, bot_name + '.json')
    json = MyJson(filename=__json_bot_file__).json

    services_classes = []
    components_classes = []

    for (key, value) in json['services'].items():
        class_name = value['cls']
        services_classes.append(class_name)
        file_url = __url__ + 'services/'  # TODO: not completed
        file = _path_ + 'services/' + class_name + '.py'
    #    urllib.request.urlretrieve(file_url, file)  # TODO: not completed

    for (key, value) in json['components'].items():
        components_classes.append(value['cls'])

    print(services_classes)
    print(components_classes)


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


def create_robot(bot_name):
    """ The first execution of this program will create the structure, files and directories needed to a
    pyro4bot robot
    """
    path = 'robots'
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, bot_name)
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
                update_robot(argument)
        else:
            argument = sys.argv[1]
            if argument == '-update':
                print("File was expected as argument.")
                os._exit(0)
            else:
                argument.replace('.json', '')  # just having the precaution of not misspelling the name
                create_robot(argument)
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
    except Exception:
        raise
