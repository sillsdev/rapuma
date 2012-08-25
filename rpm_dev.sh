#!/bin/sh
gnome-terminal --geometry=80x20 --tab --working-directory=Projects/rpm --tab --working-directory=Publishing/testArea/rpm_dev &
gedit &
nautilus ~/Publishing/testArea/rpm_dev &
libreoffice --calc ~/Projects/rpm/todo.ods
