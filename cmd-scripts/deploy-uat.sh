#!/bin/bash

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/reg-backend

PROJECT_PATH='/opt/projects/registration'
PROJECT_DIR='backend-uat'
PROJECT_DIR_PATH=${PROJECT_PATH}/${PROJECT_DIR}

cd ${PROJECT_DIR_PATH}
git checkout uat
git pull origin uat

${PROJECT_DIR_PATH}/cmd-scripts/app-run.sh up-d
ssh-agent -k

