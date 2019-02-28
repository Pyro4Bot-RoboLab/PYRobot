#!/usr/bin/env bash
sudo add-apt-repository ppa:webupd8team/atom
sudo apt update
sudo apt install python3-pip
sudo apt install atom
# for a raspberry pi Zero, don't install opencv:
# for the robot, install:
pip3 install opencv-contrib-python
sudo apt install git
pip3 install keyboard
pip3 install green
pip3 install prompt_toolkit
pip3 install PyGitHub
pip3 install -r "requirements.txt"
