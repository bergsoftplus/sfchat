# run - Run local server with --nostatic
run:
	@echo "------------------------------------------"
	@echo "***  run local server with --nostatic  ***"
	@echo "=========================================="
	@python3 manage.py runserver --nostatic --setting=sfchat.settings.local

# celery - run celery task for chat clean 
celery:
	celery  worker --beat  -A apps.chat.tasks

# help - Display callable targets.
help:
	@egrep "^# [a-z,\",=,_,-]+ - " Makefile	

# bower - Install dependences components with bower
bower:
	@cd ./bin/bower && sudo bower install

# install-local - install locally dependenses
install-local:
	@cd ./config/requirements && sudo pip3 install -r local.pip

# syncdb - Run syncdb command
syncdb:
	python3 manage.py syncdb

# sqlall - Run sqlall command
sqlall:	
	@python3 manage.py sqlall $(apps)

test:
	@python3 manage.py test
#	@python3 manage.py test apps.chat.tests.tests_models.ChatsTestCase.test_delete_message_failed

# m - Create locale
m:
	@django-admin makemessages -l ru -a

# c - Compile locale 
c:
	@django-admin.py compilemessages	

	
# style - Check PEP8 and others
PEP8IGNORE=E22,E23,E24,E302,E401
style:
	@echo "PyFlakes check:"
	@echo
	-pyflakes .
	@echo
	@echo "PEP8 check:"
	@echo
	-pep8 --ignore=$(PEP8IGNORE) .



# clean - Clean all temporary files
clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	find . -name "*.*~" -print0 | xargs -0 rm -rf
	find . -name "__pycache__" -print0 | xargs -0 rm -rf
	@echo "Clean!"


