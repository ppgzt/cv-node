# CV-Node

A CV-Node ;)

## Installation

To install in a new raspberry you should to pull the project in github and configure _cron_ to start the project in headless mode (that is without a connected monitor). This config was inspired in https://linuxconfig.org/how-to-autostart-bash-script-on-startup-on-raspberry-pi.

```bash
@reboot $project_home/bootstrap.sh '$project_home'
```

In current installation the ```$project_home``` is 'home/felpslima22/Documentos/Projects/cv-node'. *It is important to omit the first / in $project_home, because the bash interpret as directory and fail*

The db and image files are created in the ```home``` directory. For now, the folder ```$home/cv-node-data``` should be created before run the project.

## Support

### Threads in python

https://www.xanthium.in/creating-threads-sharing-synchronizing-data-using-queue-lock-semaphore-python

### Using picamera in Raspberry

https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/7

### Git Credentials in Rasp

I configured a _Fine-grained personal access tokens_ for user _ewertonsjp_ on github and stored it in local raspberry.

```bash
git config --global credential.helper store
```

### DB

https://tinydb.readthedocs.io/en/latest/