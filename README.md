xPL-PyHAL, xPL brain

xPL-PyHAL is a program that attaches itself to your xPL bus and continuously listens messages in transit.

Its role is to execute an action for a module that you define in a simple text file when he sees a message xPL related to this module.

Orders are to be placed in the directory "yamlrepo" in the form of YAML.

The file must have the extension ".yaml".

Example :

I would like to turn on the ipx800, relay 2 when I press the switch CHACON.

This is an order type "HomeEasy" (homeeasy.basic schema) to the xPL-ipx800 client

The YAML file has the following form (switch.yaml)

```
 ACTION: command
 MODULE: "0x4b92ba"
 UNIT: "9"
 TARGETXPL: "ipx800"
 TARGETMODULE: 2
```

ACTION : the command to execute

MODULE: module that initiates the sequence (here the address of the switch CHACON)

UNIT : the switch unit

TARGETXPL : the xPL client must execute the order (the client here is xPL-ipx800)

TARGETMODULE: relay target on ipx800

Another example, pressing the switch, I turn on a lamp module A2 referenced as x10. switch.yaml file contain the following values:

```
 ACTION: command
 MODULE: "0x54cd16"
 UNIT: "10"
 TARGETXPL: "heyu"
 TARGETMODULE: a2
```

Description and possible configuration

Once the file xPL-PyHAL.tgz is unzipped you will find classes and modules python which I will detail the role.

    xPL-PyHAL.py 

This is the executable that launches the centralizer xPL-PyHAL.

- Configuration : No

Launch from xPL-PyHAL directory

python xPL-PyHAL start (start daemon)

python xPL-PyHAL stop (stop daemon)

python xPL-PyHAL console (launch program in foreground. CTRL-C to stop it)

    BrainPyHAL.py 

The xPL-PyHAL main program

- Configuration : You can switch to debug mode (output to file and console logxplhal.log if you started in this mode)

# Debug : set True or False
debug = False

    Daemon.py 

Daemon class to run xPL-PyHAL in background

- Configuration : No

    Memcached.py 

Class for interacting with a Memcached server

- Configuration : Memcached server IP address and tcp port

    (localhost:11211 by default) 

def __init__(self, hostname="127.0.0.1", port="11211")

    PushingBox.py 

Class for sending notifications to the PushingBox service

- Configuration : No

    xPLmessage.py 

Class for managing xPL messages

- Configuration : No

YAML configuration files

Actions that must be performed by xPL-PyHAL must be filed in the "yamlrepo."

The text file must have the extension. Yaml

It contains the following entries:

- Action to do (choice)

ACTION : message | store | command | log

message : send notification

store : store a value somewhere

command : execute a xPL order

log : write to a log file

- address of the module that will trigger the action (required)

MODULE: « xxxxxxx »

- unit module that will trigger the action (if necessary)

UNIT: « x »

- The target to be controlled

TARGETXPL: « xxxxx »

You find examples in the directory yamlrepo (extension.sample and in the YAML.FORMAT file)

Some examples:

- Store a value "alertemode" with the key "on" for 60 seconds in a Memcached server when the module "0x4b99bb" Unit 9 triggers

```
 ACTION: store
 TARGETXPL: memcached
 MODULE: "0x4b99bb"
 UNIT: "9"
 KEY: "alertemode"
 VALUE: "on"
 TIME: "60" (défaut 900)
```

- Send a Pushingbox notification when the module "0x4b99bb '" Unit 9, match

```
 ACTION: message
 TARGETXPL: pushingbox
 MODULE: "0x4b99bb"
 UNIT: "9"
 KEY: "v9999AAAAEEEE4"
```

I hope that the examples provided will help you create your own YAML files. Of course, there may be several YAML files for a given module.

Change make onfly, no need to restart the daemon xPL-PyHAL.
