#!/usr/bin/python
import os
import sys

##Virtualenv Settings
try:
	activate_this = '/home/med/municipal_app/bin/activate_this.py'
	execfile(activate_this, dict(__file__=activate_this))
	##os.environ.setdefault("ProductionConfig", "project.config")
	os.environ['ProductionConfig'] = '.project.config'
	##Replace the standard out
	sys.stdout = sys.stderr

	##Add this file path to sys.path in order to import settings
	sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))

	##Add this file path to sys.path in order to import app
	sys.path.append('/home/med/municipal_app/app/ODMunicipalityTools/municipal_app/')


	##Create appilcation for our app
	from project import app as application
except:
	##Virtualenv Settings
	activate_this = '/home/appuser/municipality_tools/municipality_tools/bin/activate_this.py'
	execfile(activate_this, dict(__file__=activate_this))
	##os.environ.setdefault("ProductionConfig", "project.config")
	os.environ['ProductionConfig'] = '.project.config'
	##Replace the standard out
	sys.stdout = sys.stderr

	##Add this file path to sys.path in order to import settings
	sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))

	##Add this file path to sys.path in order to import app
	sys.path.append('/home/appuser/municipality_tools/municipality_tools/ODMunicipalityTools/municipal_app/')


	##Create appilcation for our app
	from project import app as application