#!/usr/bin/python
# Created by: Daniel Asay 
# Last edit: November 30th



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
import bidsconvert
import codecs


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
						choices = ['functional and fieldmaps', 'anatomical'], #removing diffusion and all for now.
					),
			]
			modalitiesAnswer = inq.prompt(modalities)
			# this logic checks for the number of choices made. This is simply to make the data more easily displayable and readable by the user
			if len(modalitiesAnswer['modalities']) == 1:
				modalityAnswer = modalitiesAnswer['modalities'][0]
				modalityLen = 1
			elif len(modalitiesAnswer['modalities']) == 2:
				modalityAnswer = modalitiesAnswer['modalities'][0] + " and " + modalitiesAnswer['modalities'][1]
				modalityLen = 2
			elif len(modalitiesAnswer['modalities']) == 3:
				modalityAnswer = 'all'
				modalityLen = 3
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
	if modalityAnswer == 'all':
		modalityAnswer = 'functional and fieldmaps and anatomical'
#	finalAns = ""
#	if "functional" in modalityAnswer:
#		finalAns.append("bold")
#	if "anatomical" in modalityAnswer:
#		finalAns.append(",T1w")
	return modalityAnswer, modalityLen

# this function exists to validate that the chosen study has a valid raw directory to use.

def validateRawDir(study):
		if rawStudyPaths[study] == "":
			return False
		else:
			return True

def validateDir(path):
	if not os.path.isdir(path):
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
						message = "Choose from the following formats",
						choices = ['prun nifti files', 'regular run nifti files', 'niftis converted from raw dicoms'], # removed 'all' option for now
					),
			]
			formatsAnswer = inq.prompt(formats)
			# this logic checks for the number of choices made. This is simply to make the data more easily displayable and readable by the user
			if len(formatsAnswer['formats']) == 1:
				formatAnswer = formatsAnswer['formats'][0]
			elif len(formatsAnswer['formats']) == 2:
				formatAnswer = formatsAnswer['formats'][0] + " and " + formatsAnswer['formats'][1]
			elif len(formatsAnswer['formats']) == 3:
				formatAnswer = formatsAnswer['formats'][0] + " and " + formatsAnswer['formats'][1] + " and " + formatsAnswer['formats'][2]
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
		if not validateDir(pathAnswer):
			print("It looks like the path you entered does not exist.\nVerify the path's existence and run the script again.")
			sys.exit()

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
				print("Study Prefix Confirmed.\n")
				time.sleep(.5)
				break
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
				print("You did not confirm your selection. Please try again.")
				time.sleep(1.5)
				continue

	# get the tasks for the study

	while True:
		try:
			taskNames = [
				inq.Text('taskNames',
						message = "Please list all the fmri tasks in this study, separated by spaces (e.g. cuff visual rest1)",
					),
			]
			tasksAnswer = inq.prompt(taskNames)
			taskAnswer = tasksAnswer['taskNames']
			taskConfirmation = {
				inq.Confirm('taskConfirmation',
						message="You've entered " + Style.BRIGHT + Fore.BLUE + taskAnswer + Style.RESET_ALL + " as the prefix. Is that correct?",
					),
			}
			confirmationAnswer = inq.prompt(taskConfirmation)
			if confirmationAnswer['taskConfirmation'] == True:
				print("Study Tasks Entry Confirmed.\n")
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
						"Prefix":[prefixAnswer],
						"Tasks": [taskAnswer]})
	#print(df2)
	df = df.append(df2, ignore_index=True)
	#print(df)
	df.to_csv('/PROJECTS/REHARRIS/studies.csv', index=False)
	#df.to_csv('~/Desktop/studies.csv', index=False)
	print("\nYour study has been successfully added to the database!\nYou will now be redirected to the starting prompt...\n")
	sleep(6)

	return nameAnswer, pathAnswer, rawAnswer, prefixAnswer, taskAnswer


# get the desired BIDS dir from the user manually, or use the default of one step above the raw directory.

def getBIDSDir(rawDirPath, study):
	# get the user input for the desired BIDS directory
	while True:
		try:
			bidsDir = [
				inq.Text('bidsDir',
						message = "Enter the full path to BIDS output directory. Press enter for default (one step above raw)",
					),
			]
			pathAnswer = inq.prompt(bidsDir)
			bidsAnswer = pathAnswer['bidsDir']
			if not bidsAnswer:
				bidsAnswer = 'default'
			bidsConfirmation = {
				inq.Confirm('bidsConfirmation',
						message="You've entered " + Style.BRIGHT + Fore.BLUE + bidsAnswer + Style.RESET_ALL + " as the bids directory. Is that correct?",
					),
			}
			confirmationAnswer = inq.prompt(bidsConfirmation)
			if confirmationAnswer['bidsConfirmation'] == True:
				print("BIDS Entry Confirmed.\n")
				time.sleep(.5)
				break
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
				print("You did not confirm your selection. Please try again.")
				time.sleep(1.5)
				continue

	if bidsAnswer == 'default':
		counter = 0
		slash = "/"
		for char in reversed(rawDirPath):
			if char != slash:
				counter -= 1
			else:
				break
		bidsAnswer = rawDirPath[:counter]
		today = str(dt.date.today())
		bidsAnswer = bidsAnswer + f"BIDS_{today}"
		return bidsAnswer


def chopVolumes(modality):
	print("Would you like to remove any volumes from the beginning of your functional runs?\nPlease note that prun and regular run files have generally already had volumes removed. Check your specific study's data to verify.")
	while True:
		try:
			chopVols = [
				inq.text('chopVols',
						message = "If so, please enter the number here. If not, please enter 0."
					),
			]
			volumesAnswer = inq.prompt(chopVols)
			volumeAnswer = volumesAnswer['copVols']
			volumesConfirmation = {
				inq.Confirm('volumesConfirmation',
						message="You've entered " + Style.BRIGHT + Fore.BLUE + volumeAnswer + Style.RESET_ALL + " as your volumes to chop. Is that correct?",
					),
			}
			confirmationAnswer = inq.prompt(volumeConfirmation)
			confirmationType = type(confirmationAnswer).__name__
			if type(confirmationAnswer) != "int":
				print("you did not enter an integer. please try again.")
				time.sleep(1.5)
				continue
			if confirmationAnswer['volumesConfirmation'] == True:
				print("Volumes to Chop Confirmed.\n")
				time.sleep(.5)
				break
			else:
				raise ValueError("You did not confirm your selection. Please try again.")
		except ValueError:
			print("You did not confirm your selection. Please try again.")
			time.sleep(1.5)
			continue

	return 	volumeAnswer	

# example
#fslroi sub-opi030pre-prun01_task-cuff_bold.nii sub-opi030pre-prun01_task-cuff_bold.nii 10 480	

# 6. Make bidsify and copy into discrete functions (makes the script more robust and readable.)
# ****** This will make use of the bidsmanager library. I will take all of the info that I've gathered
# from the user, and then create a csv file with the necessary info for bidsmanager. That will include:
# subject name, session, modality, full path to file, task (can be left blank for T1)

def bidsify(name, path, modality, niftiFormat, modalityLen, bidsDir, numVolsToChop):


	# go to the raw path for the selected study
	os.chdir(path)
	#read in the studies csv file
	studies = pd.read_csv("/PROJECTS/REHARRIS/studies.csv")

	today = str(dt.date.today())
		
	# pull out all of the relevant information from the csv file and put it into individual variables

	subset, prefix, rawDicomFormat, tasks= pullInfo(studies, name)

	taskList = tasks.split(' ')

	# get list of all the subjects that need to be run in the raw directory
	subjects = []
	for file in os.listdir():
		if file.startswith(str(prefix)):
			subjects.append(file)
			subjects.sort()

## Check to see if there are any new subjects to run. If not, kill the script.
	
	bidsAnswer, mostRecentBids, newSubs = addNewSubjects(path, subjects, name)

	if bidsAnswer == 'add new subjects to existing BIDS directory':
		bidsDir = f'BIDS_{mostRecentBids}'
		os.rename(bidsDir, f'BIDS_{today}')
		subjects = newSubs
	else:
		if os.path.isdir(bidsDir) is False:
			os.makedirs(bidsDir)

	# print all messages both to stdout and logfile

	if os.path.isdir(f"{rawDirectory}/bidslogs") is False:
		os.makedirs(f"{rawDirectory}/bidslogs")
	today = str(dt.date.today())

	f = open(f'{rawDirectory}/bidslogs/logfile_{today}.txt', 'w')
	backup = sys.stdout
	sys.stdout = Tee(sys.stdout, f)


	# create the scaffold of the bids manager csv file
	columns = ['subject', 'session', 'modality', 'file', 'task']

	filename = f"bidsconvert_{name}_{today}.csv"

	# create the csv file for bidsconvert

	bidsCSV(filename, columns)

    # read in the csv file as a pandas dataframe

	bidsDF = pd.read_csv(filename)



    # add the session number to the bidsDir csv file. **** This will have to be updated manually if 
	# someone wants something other than 1. 

	bidsDF['session'] = '1'

    # append all the subjects to the subject column. This will append the subject several times,
    # depending on if the user selected several modalities

    # the addInfo function is doing the bulk of the work here. 

	bidsDF = addInfo(bidsDF, subjects, modality, path, taskList)

	

	# write the final dataframe to the csv file	

	bidsDF.to_csv(filename, index=False)


	with open(filename, 'r') as csvfile:
		datareader = cv.reader(csvfile)
		counter = 0
		for row in datareader:
			if counter == 0:
				counter += 1
				continue
			bidsconvert.bidsify(row, bidsDir, niftiFormat, numVolsToChop)

	sys.stdout = backup

	

# this function checks if a BIDS directory already exists for a given study. If it does, it compares the date of the most recent BIDS to
# today's date. If the dates are different, it will get a list of all the subjects in the most recent BIDS directory and return the list

def addNewSubjects(path, subjects, studyName):
	# go into the study's main directory and see if and BIDS directories exist. If not, return 0's and proceed with bidsifying
	os.chdir(f"{path}/..")
	today = dt.date.today()
	bidsDirs = []
	for file in os.listdir():
		if file.startswith('BIDS_20'):
			bidsDirs.append(file)
	if not bidsDirs:
		return 0, 0, 0

	# if there are BIDS directories, find the most recent one, go into the directory and get a list of all the subjects.
	# that list will be used for a comparison later.
	bidsDates = []
	for bids in bidsDirs:
		date = bids[5:]
		date_object = dt.datetime.strptime(date, '%Y-%m-%d').date()
		bidsDates.append(date_object)
	mostRecent = str(max(bidsDates))
	strToday = str(today)
	if mostRecent == strToday:
		print(f"{studyName} was at least partially bidsified today.\nIf you'd like to start from scratch, delete the BIDS_{strToday} directory.\nResuming program...")
		time.sleep(15)
	os.chdir(f"BIDS_{mostRecent}")
	prevSubs = []
	for file in os.listdir():
		if file.startswith('sub-'):
			prevSubs.append(file)
	prevSubs.sort()

	# compare the list of subjects from most recent BIDS directory with the list of subjects given from study csv file.
	# 
	prevSubsNew = [sub[4:] for sub in prevSubs]
	newSubs = []
	for element in subjects:
		if element not in prevSubsNew:
			newSubs.append(element)
	numNewSubs = len(newSubs)

	# if there are no new subjects, ask the user if they would like to re-bidsify.

	if numNewSubs == 0:
		print(f"{studyName} was bidsified on {mostRecent} and 0 new subs have been added to the raw directory.")
		zeroNewConfirmation = {
		inq.Confirm('zeroNewConfirmation',
				message="Would you like to re-bidsify?",
			),
		}
		confirmationAnswer = inq.prompt(zeroNewConfirmation)
		if confirmationAnswer['zeroNewConfirmation'] == True:
			print("Bidsify Selection Confirmed. Re-bidsifying...\n")
			time.sleep(.5)
			return "", "", ""
		else:
			print("Bidsify Selection Confirmed. Will not re-bidsify. Exiting program...")
			time.sleep(2)
			sys.exit()

	else:
	# ask user if they would like to re-bidsify subjects or add new subs to previously bidsified and update the date
	
		while True:
			print("*****PLEASE SELECT JUST ONE RESPONSE*****\n")
			print(f"{studyName} was bidsified on {mostRecent}. {numNewSubs} new subs are in the raw directory.")
			try:
				bidsOptions = [
					inq.Checkbox('bidsOptions',
							message = "How would you like to proceed?",
							choices = ['add new subjects to existing BIDS directory', 're-bidsify all subjects'],
						),
				]
				bidssAnswer = inq.prompt(bidsOptions)
				bidsAnswer = bidssAnswer['bidsOptions']
				if 're-bidsify' in bidsAnswer and 'existing' in bidsAnswer:
					print("You selected more than one answer. Please select only one.")
					continue
				bidsConfirmation = {
					inq.Confirm('bidsConfirmation',
							message="You've selected " + Style.BRIGHT + Fore.BLUE + str(bidsAnswer) + Style.RESET_ALL + ". Is that correct?",
						),
				}
				confirmationAnswer = inq.prompt(bidsConfirmation)
				if confirmationAnswer['bidsConfirmation'] == True:
					print("Bidsify Selection Confirmed.\n")
					time.sleep(.5)
					break
				else:
					raise ValueError("You did not confirm your selection. Please try again.")
			except ValueError:
					print("You did not confirm your selection. Please try again.")
					time.sleep(1.5)
					continue	

		return bidsAnswer, mostRecent, newSubs

# this function serves as a helper in bidsify() to pull the relevant information from the studies.csv file

def pullInfo(csvFile, study):
	subset = csvFile.loc[csvFile['Study_Name'] == study]
	prefix = subset.iloc[0]['Prefix']
	rawDicomFormat = subset.iloc[0]['Raw_Format']
	tasks = subset.iloc[0]['Tasks']
	return subset, prefix, rawDicomFormat, tasks

# this function creates the csv file for bidsmanager

# might have to turn this into a pandas dataframe that gets written as a csv file later.

def bidsCSV(file, columns):
	with open(file, 'w') as csvfile:
		csvWriter = cv.writer(csvfile)
		csvWriter.writerow(columns) 

# this function concatenates each subject with the path to the raw directory from that study. it returns a list.

def addFiles(subjects, path):
	subPaths = []
	for sub in subjects:
		newPath = "".join([path, "/", sub])
		subPaths.append(newPath)
	return subPaths


# this function will prepend a specified string to every element in a given list

def prepend(array, str):
	str += '{0}'
	newList = [str.format(i) for i in array]
	return(newList)

# this function creates and returns a pandas dataframe with all of the subject, modality and task information. That dataframe gets appended
# to the larger dataframe in bidsDF

def addInfo(masterDF, subjects, modality, path, tasks):
	# if the user only wants functional data to be bidsified, then a dataframe of all the subjects and modality 'bold' is created
	if modality == 'functional and fieldmaps':
		for task in tasks:
			modalityList = []
			counter = 0
			while counter < len(subjects):
				modalityList.append('bold')
				counter += 1
			df = pd.DataFrame(subjects, columns=['subject'])
			df['session'] = '1'
			df['modality'] = modalityList
			subPath = addFiles(subjects, path)
			df['file'] = subPath
			df['task'] = task
			masterDF = masterDF.append(df, ignore_index=True)
		return masterDF

	# if the user only wants anatomical data to be bidsified, then a dataframe of all the subjects and modality 'T1w' is created
	elif modality == 'anatomical':
		modalityList = []
		counter = 0
		while counter < len(subjects):
			modalityList.append('T1w')
			counter += 1
		df = pd.DataFrame(subjects, columns=['subject'])
		df['modality'] = '1'
		df['session'] = modalityList
		subPath = addFiles(subjects, path)
		df['file'] = subPath
		df['task'] = 'anat'
		return df

	# if the user wants both functional and anatomical data to be bidsified, then a dataframe of all subjects with 'bold' immediately followed
	# by all subjects with 'T1w' 
	else: #get a list for bold
		for task in tasks:
			modalityListBold = []
			counter = 0
			while counter < len(subjects):
				modalityListBold.append('bold')
				counter += 1
			df1 = pd.DataFrame(subjects, columns=['subject'])
			df1['session'] = '1'
			df1['modality'] = modalityListBold
			subPath = addFiles(subjects, path)
			df1['file'] = subPath
			df1['task'] = task
			masterDF = masterDF.append(df1, ignore_index=True)

		modalityListAnat = [] # get list for anat
		counter = 0
		while counter < len(subjects):
			modalityListAnat.append('T1w')
			counter += 1
		df2 = pd.DataFrame(subjects, columns=['subject'])
		df2['session'] = '1'
		df2['modality'] = modalityListAnat
		subPath = addFiles(subjects, path)
		df2['file'] = subPath

		# combine the two lists
		masterDF = masterDF.append(df2, ignore_index=True)


		return masterDF


# this function will check the finished BIDS directory for any empty directories
# It will print the list of empty directories out to the terminal and also
# spit out a text file for future reference.

def checkForEmptyBids(bidsDir):
	os.chdir(bidsDir)
	emptyDirs = []
	for directory in os.listdir():
		dirSize = get_dir_size(directory)
		if dirSize == 0:
			print(f"BIDS folder for {directory} is empty. check before running a BIDS app.")
			emptyDirs.append(file)
	with open('empty_directories.txt', 'w') as empty:
		for line in lines:
			empty.write(f"{line}\n")


# calculate the size of a given directory

def getDirSize(path='.'):
	total = 0
	with os.scandir(path) as it:
		for entry in it:
			if entry.is_file():
				total += entry.stat().st_size
			elif entry.is_dir():
				total += get_dir_size(entry.path)
	return total

# 7. Check timestamp in database and compare to timestamp of data in raw, running only the subjects that have been added since last qc run.
# ****** this is an internal feature/function to be imbedded in the bidsify and copy functions mentioned above.

def checkTimestamp():
	pass

# this class serves to print prompts to terminal and also save it in a logfile

class Tee(object):
	def __init__(self, *files):
		self.files = files
	def write(self, obj):
		for f in self.files:
			f.write(obj)

# get the info from the csv file
rawStudyPaths, csv = loadStudies()

# get the selcted study and its directory path
selectedStudy, rawDirectory = selectStudy(rawStudyPaths)

# get the modality
modality, modalityLen = getModality(selectedStudy)

if modality != 'anatomical':
	# get the nifti format
	niftiFormat = getFormat()
else:
	niftiFormat = ""

bidsDir = getBIDSDir(rawDirectory, selectedStudy)

numVolsToChop = chopVolumes(modality)

bidsify(selectedStudy, rawDirectory, modality, niftiFormat, modalityLen, bidsDir, numVolsToChop)

#checkForEmptyBids(bidsDir)

#





