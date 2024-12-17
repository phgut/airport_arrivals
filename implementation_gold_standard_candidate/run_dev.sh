#/bin/bash

cp -n ./api_server/builder/entrypoint.sh.template ./api_server/builder/entrypoint.sh
cp -n ./api_server/builder/.env.template ./api_server/builder/.env
cp -n ./ui/.env.template ./ui/.env

set -x
docker compose up -d --build 
cd ui && npm start