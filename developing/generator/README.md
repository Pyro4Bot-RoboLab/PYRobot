# Generate a _PYRO4BOT_

## Getting started



## Prerequisites
* Python 3.5 or above
* Having your robot already built
* Download the _Pyro4Bot_ project into the machine
* Set up the environment folder of Pyro4Bot in your machine

## Installing
If you don't have the environment setted up, the programm will show an error message like this:
```
ERROR: PYRO4BOT_HOME not setted
please type export PYRO4BOT_HOME=<DIR> to set it up
```
To set it up, type the path of the program pyro4bot downloaded. For example:
```
export PYRO4BOT_HOME=/usr/my_user/pyro4bot/developing
```
or modify your _.bash_profile_ file to keep the environment permanently in the machine.


### First step
Execute the python file with a name for your custom robot like this:
```
python3 generate_robot.py my_robot
```
This is also valid:
```
./generate_robot.py my_robot
```

### Second step
Then, you will have a new directory named _*robots*_ with your robot <_my_robot_> inside, it's just
another folder with the name of your robot.

That folder should have a structure like the following:
```
/developing
/init
    /generate_robot.py
    /robots
        /my_robot
            /start.py
            /model.py
                /my_robot.json
            /components
                /template_component.py
            /services
                /template_service.py
            /clients
                /class_client_robot.py
                /class_my_robot.py
            /gui_start.py
```

The description of your robot is the json file, _my_robot.json_, there you must complete with the 
components and services required to run your robot.

Your model robot json file will be something like this:
```
{
   "NODE":{
      "name":"my_robot",
      "ethernet":"wlan0"
    },
   "services":{
        "servicename":{"cls":"classname","required_utility":"id_of_utility"}
   },
   "components":{
        "componentname":{"cls":"classname", "required_dependency":"value_of_dependencies"}
    }
}
```

And it should have the components and services described. There you have an example:
```
{
   "node":{
      "name":"my_robot",
      "ethernet":"wlan0"
    },
   "services":{
        "picam":{"cls":"picam","ethernet":"<ethernet>","width":640,"height":480}
   },
   "components":{
        "infrared":{"cls":"infrared","IR":[0,0,0,0],"frec":0.02},
        "basemotion":{"cls":"basemotion","BASE":[0,0],"frec":0.03},
        "pantilt":{"cls":"pantilt","PT":[90,90],"frec":0.03}
    }
}
```


### Third step

Once you have your json file completed, you can generate the rest of required elements of your robot just typing:
```
./generate_robot.py my_robot -u
```
It will download the required elements from our [repository](https://github.com/Pyro4Bot-RoboLab/Components) if there are developed.
For the json of the last example, it will generate:

```
/developing
/init
    /generate_robot.py
    /robots
        /my_robot
            /start.py
            /model.py
                /my_robot.json
            /components
                /stable
                    /infrared
                        /infrared.py
                    /basemotion
                        /basemotion.py
                    /pantilt
                        /pantilt.py
                /template_component.py
            /services
                /stable
                    /picam_socket
                        /picam_socket.py
                /template_service.py
            /clients
                /class_client_robot.py
                /class_my_robot.py
            /gui_start.py
```
### Third step (second version)
As you can see in the default services and components folders, there are templates files to the user,
 to use them and create your customized elements for your bot.
This way you won't need to update the robot to make it functional, but still we encourage you to use
the same commands.

It will check the components and services of your robot, and those elements you develop would prevail over ours.


### Four step
Go to your robot's folder and run:
```
./start.py
```


## _About_

_This is an educational research project of [**RoboLab**](https://robolab.unex.es/), a researcher group from the School 
of Technology of Cáceres (Spain) of the University of Extremadura._
