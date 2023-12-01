
<h1 align="center"> University - Registration Portal </h1> <br>
<p align="center">
  <a href="https://gitpoint.co/">
    <img alt="Logo " title="Logo of the project" src="https://my.um.edu.sa/portal/static/media/Logo-sm.84c5f7e4.png" width="450">
  </a>
</p>

<p align="center">
  Django Backend for Almareefa University.
</p>

## Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Steps to run the project](#steps-to-run-the-project)
- [Deployment](#deployment)


# Introduction

The university project is a project for handling all services used for all offline process to use in an online system to make it easier to process student without need to make everything into the university directly.


# Requirements
------------

Python 3.8 supported.

Django 3.0 supported.

----

Setup
# Steps to run the project

## Install packages

````bash
    pip install .requirements.txt
````

## Prepare and Runserver
```bash
    ./manage.py migrate --settings=university.settings.local
    ./manage.py runserver --settings=university.settings.local
```

## Create Superuser
```bash
    ./manage.py createsuperuser --settings=university.settings.local
```

## Run celery Task
**Note:** should be change settings in `university/settings/celery.py` to local
``` 
    celery --app=university.settings.celery:app worker --loglevel=INFO --concurrency=15 -B
    
```


# Deployment

#### For DEV Environment

```
    cmd-scripts/deploy-dev.sh
```

#### For UAT Environment

```
    cmd-scripts/deploy-uat.sh
```
#### For Production Environment

```
    cmd-scripts/deploy-prod.sh
```

## Application Run
```
    cmd-scripts/app-run.sh up
    cmd-scripts/app-run.sh up-d
```

## Application Down
```
    cmd-scripts/app-run.sh down
```

## Load Static
```
    cmd-scripts/app-load.sh static
```

## Apply Migrations
```
    cmd-scripts/app-load.sh migrate
```
