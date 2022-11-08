#!/usr/bin/python
# Created by: Daniel Asay 
# Last edit: October 25th

# the database aspect of this script may be more ambitious than is really feasible right now...

# import necessary libraries`

import inquirer as inq
import datetime as dt
import os
import sys
import time
import csv as cv
import pandas as pd
import subprocess
import shutil
from tqdm import tqdm
from yaspin import yaspin
from pprint import pprint
from colorama import Fore
from colorama import Style
from time import sleep
from bidsmanager.read import read_csv
from bidsmanager.read.dicom_reader import read_dicom_directory
from bidsmanager.write.dataset_writer import write_dataset


# This script is a new version of the beforefmriprep scripts. 

#Things this script will have:

# 1. Create user-prompt for running copying/bidsifying anat, func or fmap data


# this function serves to load in the list of studies and their raw directories from the csv file stored on the server

def loadStudies():
	#df = pd.read_csv("~/Desktop/studies.csv")
	df = pd.read_csv("/PROJECTS/REHARRIS/studies.csv")
	names = list(df['Study_Name'])
	rawPaths = list(df['Raw_Path'])
	pairs = dict(zip(names, rawPaths))
	return pairs, df


# this function will ask the user to select a study they would like to bidsify from the generated list. 

def selectStudy(studyPaths):
	names = list(studyPaths.keys())
	names.append('add new study')
	while True:
		try:
			studies = [
				inq.List('studies',
						message = "Which study would you like to bidsify?",
						choices = names
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
				print("Study Selection Confirmed.\n")
				sleep(.5)
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
				print("You did not confirm your selection. Please try again.")
				sleep(1.5)
				continue
		if studyAnswer == "explosive sync":
			studyAnswer = "explosiveSync"
		elif studyAnswer == "bacpac best":
			studyAnswer = "bacpacBest"
		elif studyAnswer == "add new study":
			addStudy()
			#os.system("python3 ~/Documents/Michigan/bidsify/bidsify.py")
			os.system("python3 ~/bidsify/bidsify.py")
			sys.exit()
		if validateRawDir(studyAnswer) == True:
			break
		else:
			print("The study you selected does not have a valid raw directory.\nSelect a different study or add a valid raw directory for " + studyAnswer + ".")
			time.sleep(1.5)
			continue
	rawDir = studyPaths[studyAnswer]
	return studyAnswer, rawDir

# this function will ask the user to select the modality types they would like to bidsify

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
				print("Modality Selection Confirmed.\n")
				time.sleep(.5)
				break
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
				print("You did not confirm your selection. Please try again.")
				time.sleep(1.5)
				continue
	return modalityAnswer

# this function exists to validate that the chosen study has a valid raw directory to use.

def validateRawDir(study):
		if rawStudyPaths[study] == "":
			return False
		else:
			return True



# 2. Ask user if it wants niftis created from raw dicoms, or the run_01.nii, prun_01.nii or all of the above.

# this function will ask the user to choose from several options regarding how they want their data copied.

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
				print("Format Selection Confirmed.\n")
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

# this function may not be relevant, theoretically this info will be in the csv file

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
				print("Raw Dicom Format Selection Confirmed.\n")
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

# this supports the user in adding a new study to the list. It asks for the name, raw data path and the form the raw data comes in.

def addStudy():
	while True:

		# get the new study's name

		try:
			newName = [
				inq.Text('newName',
						message = "What's the name of the new study?",
					),
			]
			namesAnswer = inq.prompt(newName)
			nameAnswer = namesAnswer['newName']
			nameConfirmation = {
				inq.Confirm('nameConfirmation',
						message="New study name: " + Style.BRIGHT + Fore.BLUE + nameAnswer + Style.RESET_ALL + ". Is that correct?",
					),
			}
			confirmationAnswer = inq.prompt(nameConfirmation)
			if confirmationAnswer['nameConfirmation'] == True:
				print("New Study Name Confirmed.\n")
				time.sleep(.5)
				break
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
			print("You did not confirm your selection. Please try again.")
			time.sleep(1.5)
			continue

		# get the new study's path to raw directory

	while True:
		try:
			newPath = [
				inq.Text('newPath',
						message = "Please enter the full path to the study's raw directory",
					),
			]
			pathsAnswer = inq.prompt(newPath)
			pathAnswer = pathsAnswer['newPath']
			pathConfirmation = {
				inq.Confirm('pathConfirmation',
						message="New study raw path: " + Style.BRIGHT + Fore.BLUE + pathAnswer + Style.RESET_ALL + ". Is that correct?",
					),
			}
			confirmationAnswer = inq.prompt(pathConfirmation)
			if confirmationAnswer['pathConfirmation'] == True:
				print("New Raw Path Confirmed.\n")
				time.sleep(.5)
				break
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
			print("You did not confirm your selection. Please try again.")
			time.sleep(1.5)
			continue

	# get the format that the new study's dicoms come in

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
				print("Raw Dicom Format Selection Confirmed.\n")
				time.sleep(.5)
				break
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
				print("You did not confirm your selection. Please try again.")
				time.sleep(1.5)
				continue

	# get the prefix for the subjects in the study

	while True:
		try:
			prefixTypes = [
				inq.Text('prefixTypes',
						message = "What is the prefix for the subjects in the raw dir? (e.g. 'opi' for opioid study)",
					),
			]
			prefixesAnswer = inq.prompt(prefixTypes)
			prefixAnswer = prefixesAnswer['prefixTypes']
			prefixConfirmation = {
				inq.Confirm('prefixConfirmation',
						message="You've entered " + Style.BRIGHT + Fore.BLUE + prefixAnswer + Style.RESET_ALL + " as the prefix. Is that correct?",
					),
			}
			confirmationAnswer = inq.prompt(prefixConfirmation)
			if confirmationAnswer['prefixConfirmation'] == True:
				print("Raw Dicom Format Selection Confirmed.\n")
				time.sleep(.5)
				break
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
				print("You did not confirm your selection. Please try again.")
				time.sleep(1.5)
				continue

	df = pd.read_csv("/PROJECTS/REHARRIS/studies.csv")
	#df = pd.read_csv("~/Desktop/studies.csv")
	df2 = pd.DataFrame({"Study_Name":[nameAnswer],
						"Raw_Path":[pathAnswer],
						"Raw_Format":[rawAnswer],
						"Last_Copied":"",
						"Prefix":[prefixAnswer]})
	#print(df2)
	df = df.append(df2, ignore_index=True)
	#print(df)
	df.to_csv('/PROJECTS/REHARRIS/studies.csv', index=False)
	#df.to_csv('~/Desktop/studies.csv', index=False)
	print("\nYour study has been successfully added to the database!\nYou will now be redirected to the starting prompt...\n")
	sleep(6)

	return nameAnswer, pathAnswer, rawAnswer, prefixAnswer


# get the desired BIDS dir from the user manually, or use the default of one step above the raw directory.

def getBIDSDir():
	pass

# 6. Make bidsify and copy into discrete functions (makes the script more robust and readable.)
# ****** This will make use of the bidsmanager library. I will take all of the info that I've gathered
# from the user, and then create a csv file with the necessary info for bidsmanager. That will include:
# subject name, session, modality, full path to file, task (can be left blank for T1)

def bidsify(name, path, modality, niftiFormat):


	# go to the raw path for the selected study
	os.chdir(path)
	#read in the studies csv file
	studies = pd.read_csv("/PROJECTS/REHARRIS/studies.csv")

	# pull out all of the relevant information from the csv file and put it into individual variables

	subset, prefix, rawDicomFormat = pullInfo(studies, name)

	# get list of all the subjects that need to be run in the raw directory
	subjects = []
	for file in os.listdir():
		if file.startswith(str(prefix)):
			subjects.append(file)


	# create the scaffold of the bids manager csv file
	columns = ['subject', 'session', 'modality', 'file', 'task']

	today = str(dt.date.today())

	filename = f"bidsmanager_{name}_{today}.csv"

	# create the csv file for bidsmanager

	bidsCSV(filename, columns)

    # read in the csv file as a pandas dataframe

	bidsDF = pd.read_csv(filename)

    # append all the subjects to the Subject_Name column

	for sub in subjects:
		bidsDF = bidsDF.append({'subject': sub}, ignore_index=True)


	# add the session number to the bidsDir csv file. **** This will have to be updated manually if 
	# someone wants something other than 1. 

	bidsDF['session'] = '1'

	print(bidsDF)

	# insert the modality 

# this function serves as a helper in bidsify() to pull the relevant information from the studies.csv file

def pullInfo(csvFile, study):
	subset = csvFile.loc[csvFile['Study_Name'] == study]
	prefix = subset.iloc[0]['Prefix']
	rawDicomFormat = subset.iloc[0]['Raw_Format']
	return subset, prefix, rawDicomFormat

# this function creates the csv file for bidsmanager

# might have to turn this into a pandas dataframe that gets written as a csv file later.

def bidsCSV(file, columns):
	with open(file, 'w') as csvfile:
		csvWriter = cv.writer(csvfile)
		csvWriter.writerow(columns) 

def addData(columnName, data):
	pass




# make sure you check if the data has already been copied
def copyData():
	pass

# 7. Check timestamp in database and compare to timestamp of data in raw, running only the subjects that have been added since last qc run.
# ****** this is an internal feature/function to be imbedded in the bidsify and copy functions mentioned above.

def checkTimestamp():
	pass


# get the info from the csv file
rawStudyPaths, csv = loadStudies()

# get the selcted study and its directory path
selectedStudy, directory = selectStudy(rawStudyPaths)

# get the modality
modality = getModality(selectedStudy)

# get the nifti format
niftiFormat = getFormat()


bidsify(selectedStudy, directory, modality, niftiFormat)

#print(csv)
#print(selectedStudy)
#print(directory)
#print(modality)
#print(niftiFormat)





