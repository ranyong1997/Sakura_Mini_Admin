#!/bin/sh
docker build -t sakura_mini_admin .
docker run -d --name sakura_mini_admin -p 5555:80 sakura_mini_admin
