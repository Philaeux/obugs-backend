#!/bin/bash

git pull
cd obugs && ./gradlew installdist
sudo systemctl restart obugsapi

