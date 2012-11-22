#!/bin/sh
gnome-terminal --geometry=80x20 --tab --working-directory="Projects/rapuma" &
# echo -e "Please type [. ./dev_setup.sh] to set the development paths." &
notify-send "Please type [. ./dev_setup.sh] to set the development paths."
gedit &
nautilus ~/Publishing/testArea &
#libreoffice --calc ~/Projects/rapuma/todo.ods
