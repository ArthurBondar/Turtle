#!/bin/bash

# Path of the working code directory
src=/home/arthur/Projects/Underwater-POV-Camera-Tag/WebPage/

# Path to the Apache directory
server=/var/www/html

sudo rsync -ah -progress --exclude '*.sh' $src $server