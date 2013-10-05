#!/bin/bash

rsync -av \
	--delete \
	--exclude .htaccess \
	$(pwd)/build/ \
	courses.cs.luc.edu:/var/www/vhosts/courses.cs.luc.edu/htdocs/

