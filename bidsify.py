#!/usr/bin/python
# Created by: Daniel Asay 
# Last edit: October 14th

# the database aspect of this script may be more ambitious than is really feasible right now...

# import necessary libraries`

import inquirer as inq
import os
import time
import subprocess
import shutil
from tqdm import tqdm
from yaspin import yaspin
from pprint import pprint
from colorama import Fore
from colorama import Style


# This script is a new version of the beforefmriprep scripts. 

#Things this script will have:

# 1. Create user-prompt for running copying/bidsifying anat, func or fmap data
#	***** Grab this from the qc pipeline scripts

def selectStudy(studyPaths):
	while True:
		try:
			studies = [
				inq.List('studies',
						message = "Which study would you like to bidsify?",
						choices = ['opioid', 'explosive sync', 'bacpac', 'bacpac best', 'mapp2', 'micapp', 'cpira2', 'add new study'],
					),
			]
			studiesAnswer = inq.prompt(studies)
			studyAnswer = studiesAnswer['studies']
			studyConfirmation = {
				inq.Confirm('studyConfirmation',
						message="You've selected the " + Style.BRIGHT + Fore.GREEN + studyAnswer + Style.RESET_ALL + " study. Is that correct?",
					),
			}
			confirmationAnswer = inq.prompt(studyConfirmation)
			if confirmationAnswer['studyConfirmation'] == True:
				print("Study Selection Confirmed.")
				time.sleep(.5)
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
				print("You did not confirm your selection. Please try again.")
				time.sleep(1.5)
				continue
		if studyAnswer == "explosive sync":
			studyAnswer = "explosiveSync"
		elif studyAnswer == "bacpac best":
			studyAnswer = "bacpacBest"
		elif studyAnswer == "add new study":
			addStudy()
		if validateRawDir(studyAnswer) == True:
			break
		else:
			print("The study you selected does not have a valid BIDS directory.\nSelect a different study or add a valid BIDS directory for " + studyAnswer + ".")
			time.sleep(1.5)
			continue
	rawDir = studyPaths[studyAnswer]
	return studyAnswer, rawDir

def getModality(study):
	print("\nWhen selecting modalities, you can choose more than one option.\nUse the right arrow key to check an option and the left arrow key to uncheck.\nPress enter when you're done choosing.")
	while True:
		try:
			modalities = [
				inq.Checkbox('modalities',
						message = "Which modalities would you like to bidsify from " + Style.BRIGHT + Fore.GREEN + study +  Style.RESET_ALL + "?",
						choices = ['functional and fieldmaps', 'anatomical', 'diffusion', 'all'],
					),
			]
			modalitiesAnswer = inq.prompt(modalities)
			# this logic checks for the number of choices made. This is simply to make the data more easily displayable and readable by the user
			if len(modalitiesAnswer['modalities']) == 1:
				modalityAnswer = modalitiesAnswer['modalities'][0]
			elif len(modalitiesAnswer['modalities']) == 2:
				modalityAnswer = modalitiesAnswer['modalities'][0] + " and " + modalitiesAnswer['modalities'][1]
			elif len(modalitiesAnswer['modalities']) == 3:
				modalityAnswer = 'all'
			else:
				continue
			for mode in modalitiesAnswer['modalities']:
				if mode == "all":
					modalityAnswer = 'all'
			modalityConfirmation = {
				inq.Confirm('modalityConfirmation',
						message="You've selected " + Style.BRIGHT + Fore.GREEN + modalityAnswer + Style.RESET_ALL + ". Is that correct?",
					),
			}
			confirmationAnswer = inq.prompt(modalityConfirmation)
			if confirmationAnswer['modalityConfirmation'] == True:
				print("Modality Selection Confirmed.")
				time.sleep(.5)
				break
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
				print("You did not confirm your selection. Please try again.")
				time.sleep(1.5)
				continue
	return modalityAnswer

def validateRawDir(study):
		if rawStudyPaths[study] == "":
			return False
		else:
			return True



# 2. Ask user if it wants niftis created from raw dicoms, or the run_01.nii, prun_01.nii or all of the above.
#	******* this can also be taken from the qc pipeline scripts

def getFormat():
	print("\nNow, select the format you'd like your niftis to come in.")
	print("When selecting the format, you can choose more than one option.\nUse the right arrow key to check an option and the left arrow key to uncheck.\nPress enter when you're done choosing.")
	while True:
		try:
			formats = [
				inq.Checkbox('formats',
						message = "Choose from the following formats:",
						choices = ['prun nifti files', 'regular run nifti files', 'niftis converted from raw dicoms', 'all'],
					),
			]
			formatsAnswer = inq.prompt(formats)
			# this logic checks for the number of choices made. This is simply to make the data more easily displayable and readable by the user
			if len(formatsAnswer['formats']) == 1:
				formatAnswer = formatsAnswer['formats'][0]
			elif len(formatsAnswer['formats']) == 2:
				formatAnswer = formatsAnswer['formats'][0] + " and " + formatsAnswer['formats'][1]
			elif len(formatsAnswer['formats']) == 3:
				formatAnswer = 'all'
			else:
				continue
			for form in formatsAnswer['formats']:
				if form == "all":
					formatAnswer = 'all'
			formatConfirmation = {
				inq.Confirm('formatConfirmation',
						message="You've selected " + Style.BRIGHT + Fore.GREEN + formatAnswer + Style.RESET_ALL + ". Is that correct?",
					),
			}
			confirmationAnswer = inq.prompt(formatConfirmation)
			if confirmationAnswer['formatConfirmation'] == True:
				print("Format Selection Confirmed.")
				time.sleep(.5)
				break
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
				print("You did not confirm your selection. Please try again.")
				time.sleep(1.5)
				continue
	return formatAnswer

#3. Ask user what format the raw dicoms come in (e.g. zip, tgz or don't know)
# ****** this can probably be adpated from the qc pipeline scripts as well

def rawType():
	while True:
		try:
			rawTypes = [
				inq.List('rawTypes',
						message = "What format do the raw dicoms come in?",
						choices = ['tgz', 'zip', 'not sure'],
					),
			]
			rawsAnswer = inq.prompt(rawTypes)
			rawAnswer = rawsAnswer['rawTypes']
			rawConfirmation = {
				inq.Confirm('rawConfirmation',
						message="You've selected " + Style.BRIGHT + Fore.BLUE + rawAnswer + Style.RESET_ALL + " format. Is that correct?",
					),
			}
			confirmationAnswer = inq.prompt(rawConfirmation)
			if confirmationAnswer['rawConfirmation'] == True:
				print("Raw Dicom Format Selection Confirmed.")
				time.sleep(.5)
				break
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
				print("You did not confirm your selection. Please try again.")
				time.sleep(1.5)
				continue
	return rawAnswer

# 4. Give user the option to add new study to matrix
# ***** the user portion can be taken from the qc scripts, but I will have to do some reading on python sql
# *****commands
# ***** This is where the database portion comes in. We could have a simple table that contains each study's name, path, data format and total subjects (running count), timestamp of when qc was last run
# ***** Gonna have to create a table that holds all this info

def addStudy():
	pass

# 6. Make bidsify and copy into discrete functions (makes the script more robust and readable.)
# ****** I'll have to modify the stuff in beforefmriprep01 and func_BIDS

def bidsify():
	pass


# make sure you check if the data has already been copied
def copyData():
	pass

# 7. Check timestamp in database and compare to timestamp of data in raw, running only the subjects that have been added since last qc run.
# ****** this is an internal feature/function to be imbedded in the bidsify and copy functions mentioned above.

def checkTimestamp():
	pass


rawStudyPaths = {"opioid": "/PROJECTS/REHARRIS/opioid/RAW", "explosiveSync": "/PROJECTS/REHARRIS/explosives/raw", "bacpac": "/PROJECTS/bacpac/raw", "bacpacBest": "/PROJECTS/bacpac/qa/best/BIDS", "mapp2": "/PROJECTS/MAPP/MAPP2/SUBJECTS", "cpira2": "", "add new study": "placeholder"}

selectedStudy, directory = selectStudy(rawStudyPaths)
modality = getModality(selectedStudy)
niftiFormat = getFormat()
if "raw" in niftiFormat:
	rawType()







