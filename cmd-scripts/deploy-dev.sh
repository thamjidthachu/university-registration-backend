#!/bin/bash

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/reg-backend

PROJECT_PATH='/opt/projects/registration'
PROJECT_DIR='backend-dev'
PROJECT_DIR_PATH=${PROJECT_PATH}/${PROJECT_DIR}

cd ${PROJECT_DIR_PATH}
git checkout dev
git pull origin dev

${PROJECT_DIR_PATH}/cmd-scripts/app-run.sh up-d
ssh-agent -k

