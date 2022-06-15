#!/bin/bash

cd obugs && ./gradlew installdist
sudo systemctl restart obugsapi

