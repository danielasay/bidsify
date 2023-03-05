#!/usr/bin/python

# ideally, this class/library would be able to take a csv file that has all the necessary information to create a BIDS dataset. 


import os
import pprint
import shutil
import sys
import subprocess
import time
import json as js
from colorama import Fore
from colorama import Style



def bidsify(data, bidsDir, niftiFormat, numVolsToChop):
	subject = data[0]
	session = data[1]
	modality = data[2]
	subPath = data[3]
	task = data[4]
	print("\n" + Style.BRIGHT + Fore.BLUE + "bidsifying data for subject " + subject + " " + modality  + " " + task + "...\n" + Style.RESET_ALL)
	time.sleep(.5)
	copyData(subject, modality, subPath, task, bidsDir, niftiFormat, numVolsToChop)


# I want it take all the info for a given subject, create the BIDS dir if it doesn't already exist,
# then cd into the 'func' dir for bold and 'anat' for T1w, then cd into the task for bold, then iterate
# through each run for that task, copying the desired nii file (run_01.nii, prun_01.nii or from raw) and
# the associated json file to the BIDS directory


def parseNiftiInfo(niftiInfo):
	niftiFormat = ""
	if "prun" in niftiInfo:
		niftiFormat += "prun "
	if "regular" in niftiInfo:
		niftiFormat += "run01 "
	if "raw" in niftiInfo:
		niftiFormat += "raw "
	niftiFormat = niftiFormat[:-1]
	return niftiFormat



# This function will go through each subject in the list, go into each functional task directory,
# and each task's run directory and copy the run_01.nii file to that subject's corresponding BIDS
# directory. There are several lines where edits are made to strings for BIDS compliance. 


def copyData(subject, modality, rawSubDir, task, bidsDir, niftiFormat, numVolsToChop):
	# if the modality is bold, then make a function bids directory for the subject.
	# copy data over from raw according to the user specifications. Also copy fieldmaps
	desiredNifti = parseNiftiInfo(niftiFormat)
	oldSubName = subject
	subject = modifySubName(subject)

	# if the user has specified that they want bold data bidsified, create a directory for each type of functional run

	if modality == 'bold':
			# for the given task (e.g. cuff) check if there's data for it in the subject's raw directory
		taskPath = "".join([rawSubDir, "/", "func", "/", task])

		# if if doesn't exist, tell the user and then move to next line in csv file (next subject)
		if not os.path.isdir(taskPath):
			print(subject + " does not have a " + task + " directory. Moving to next subject.")
			time.sleep(1)

		# if the path does exist and prun is in the niftiFormat variable, then create a directory dedicated to the prun nifti type and it's 
		# associated task and runs.
		if os.path.isdir(taskPath) and "prun" in niftiFormat:
			os.chdir(taskPath)
			runs = os.listdir()
			for run in runs:
				runNum = run[-2:]

				# create a new file name based on the run number, get just the subject name for creating the directory
				newFileName = f"sub-{subject}Prun{runNum}_task-{task}_{modality}.nii"
				bidsSubName = newFileName.split("_")[0]

				# create the functional directory for prun nifti at specific run and task
				funcBidsDir = "".join([bidsDir, "/", bidsSubName, "/func"])
				try:
					os.makedirs(funcBidsDir)
				except FileExistsError:
					print("")

				# go into the run directory and generate a json file
				os.chdir(run)
				if not createAndCopyJson(task, subject, modality, funcBidsDir, newFileName):
					print("json file could not be generated for subject " + subject + "'s " + task + "... no raw dicoms")
					time.sleep(1)

				# copy the phsio corrected data into bids directory and bidsify

				if not os.path.exists(f"{funcBidsDir}/{newFileName}"):
					try:
						shutil.copy(f"prun_{runNum}.nii", funcBidsDir)
						os.rename(f"{funcBidsDir}/prun_{runNum}.nii", f"{funcBidsDir}/{newFileName}")
						print(f"successfully bidsified prun file for subject {subject} {task} run{runNum}")
						time.sleep(.8)
					except FileNotFoundError:
						print("prun file does not exist for subject " + subject + " " + task)
						time.sleep(1)


					# if the user wanted to remove volumes, remove them here
					if numVolsToChop > 0:
						print(f'removing {numVolsToChop} volumes from {newFileName}...')
						totalVolumes = getTotalNumberOfVolumes(subject, newFileName, funcBidsDir)
						newTotalVols = totalVolumes - numVolsToChop
						chopVols = f'fslroi {newFileName} {newFileName} {numVolsToChop} {newTotalVols}'
						proc1 = subprocess.Popen(chopVols, shell=True, stdout=subprocess.PIPE)
						proc1.wait()
						print(f"{newFileName} now has {newTotalVols} volumes.")


				else:
					print("prun file has already been bidsified for " + subject + " " + task)
					time.sleep(1)

				
				# copy over the corresponding fieldmap data
				copyFmapData(rawSubDir, oldSubName, bidsSubName, bidsDir, task, "prun", runNum)

				# go back to the task directory in the event of multiple runs
				os.chdir(taskPath)

		#if the path does exist and regular run is in the niftiFormat variable, then create a directory dedicated to the regular run nifti type and it's 
		# associated task and runs.
		if os.path.isdir(taskPath) and "regular" in niftiFormat:
			os.chdir(taskPath)
			runs = os.listdir()
			for run in runs:
				runNum = run[-2:]
				# create a new file name based on the run number, get just the subject name for creating the directory
				newFileName = f"sub-{subject}Run{runNum}_task-{task}_{modality}.nii"
				bidsSubName = newFileName.split("_")[0]
				# create the functional directory for run nifti at specific run and task
				funcBidsDir = "".join([bidsDir, "/", bidsSubName, "/func"])
				try:
					os.makedirs(funcBidsDir)
				except FileExistsError:
					print("")
				# go into the run directory and generate a json file
				os.chdir(run)
				if not createAndCopyJson(task, subject, modality, funcBidsDir, newFileName):
					print("json file could not be generated for subject " + subject + "'s " + task + "... no raw dicoms")
					time.sleep(1)
				# copy the regular run data into bids directory and bidsify
				if not os.path.exists(f"{funcBidsDir}/{newFileName}"):
					try:
						shutil.copy(f"run_{runNum}.nii", funcBidsDir)
						os.rename(f"{funcBidsDir}/run_{runNum}.nii", f"{funcBidsDir}/{newFileName}")
						print(f"successfully bidsified regular run file for subject {subject} {task} run{runNum}")
						time.sleep(.8)
					except FileNotFoundError:
						print("prun file does not exist for subject " + subject + " " + task)
						time.sleep(1)
					# if the user wanted to remove volumes, remove them here
					if numVolsToChop > 0:
						print(f'removing {numVolsToChop} volumes from {newFileName}...')
						totalVolumes = getTotalNumberOfVolumes(subject, newFileName, funcBidsDir)
						newTotalVols = totalVolumes - numVolsToChop
						chopVols = f'fslroi {newFileName} {newFileName} {numVolsToChop} {newTotalVols}'
						proc1 = subprocess.Popen(chopVols, shell=True, stdout=subprocess.PIPE)
						proc1.wait()
						print(f"{newFileName} now has {newTotalVols} volumes.")
				else:
					print("prun file has already been bidsified for " + subject + " " + task)
					time.sleep(1)

				
				# copy over the corresponding fieldmap data
				copyFmapData(rawSubDir, oldSubName, bidsSubName, bidsDir, task, "regular run", runNum)

				# go back to the task directory in the event of multiple runs
				os.chdir(taskPath)

		#if the path does exist and regular run is in the niftiFormat variable, then create a directory dedicated to the raw dicom nifti type and it's 
		# associated task and runs.	
		if os.path.isdir(taskPath) and "raw" in niftiFormat:
			os.chdir(taskPath)
			runs = os.listdir()
			for run in runs:
				runNum = run[-2:]
				# create a new file name based on the run number, get just the subject name for creating the directory
				newFileName = f"sub-{subject}Raw{runNum}_task-{task}_{modality}.nii"
				bidsSubName = newFileName.split("_")[0]
				# create the functional directory for raw nifti at specific run and task
				funcBidsDir = "".join([bidsDir, "/", bidsSubName, "/func"])
				try:
					os.makedirs(funcBidsDir)
				except FileExistsError:
					print("")
				# go into the run directory and generate a json file
				os.chdir(run)
				if not createAndCopyJson(task, subject, modality, funcBidsDir, newFileName):
					print("json file could not be generated for subject " + subject + "'s " + task + "... no raw dicoms")
					time.sleep(1)
				# copy the raw nifti data into bids directory and bidsify
				if not os.path.exists(f"{funcBidsDir}/{newFileName}"):
					# look for old naming convention of raw nifti data
#					try:
#						shutil.copy(f"sub-{oldSubName}_task-{task}_{modality}.nii", funcBidsDir)
#						os.rename(f"{funcBidsDir}/sub-{oldSubName}_task-{task}_{modality}.nii", f"{funcBidsDir}/{newFileName}")
#						print(f"successfully bidsified raw dicom nifti file for subject {subject} {task} run{runNum}")
#						time.sleep(.8)
#					except:
						# see if you can embed a try statement here to copy over data with the new dcm2niix command
					try:
						shutil.copy(newFileName, funcBidsDir)
						print(f"successfully bidsified raw dicom nifti file for subject {subject} {task} run{runNum}")
						time.sleep(.8)
					except FileNotFoundError as e:
						print(e)
						#print("dcm2niix failed for subject " + subject + " " + task + ", which means no raw dicom nifti or json file.\nTry again manually in the terminal.")
						# try to run dcm2niix again
						print('Trying to run dcm2niix again...')
						if os.path.isdir('dicom'):
							os.chdir('dicom')
							dcm2niix(task, oldSubName, modality, bidsSubName)
							os.chdir('..')
							os.rename(f"{bidsSubName}_task-{task}_{modality}.nii", newFileName)
							shutil.copy(newFileName, funcBidsDir)
							print(f"successfully bidsified raw dicom nifti file for subject {subject} {task} run{runNum}")
							time.sleep(1)
						else:
							print(f"Subject {oldSubName}'s {task} task run {runNum} doesn't have raw dicoms in it's directory.\nUnable convert from raw dicoms to nifti.")


					# if the user wanted to remove volumes, remove them here
					if numVolsToChop > 0:
						print(f'removing {numVolsToChop} volumes from {newFileName}...')
						totalVolumes = getTotalNumberOfVolumes(subject, newFileName, funcBidsDir)
						newTotalVols = totalVolumes - numVolsToChop
						chopVols = f'fslroi {newFileName} {newFileName} {numVolsToChop} {newTotalVols}'
						proc1 = subprocess.Popen(chopVols, shell=True, stdout=subprocess.PIPE)
						proc1.wait()
						print(f"{newFileName} now has {newTotalVols} volumes.")
				else:
					print("raw dicom nifti file has already been bidsified for " + subject + " " + task)
					time.sleep(1)

				os.chdir(taskPath)
				# copy over the corresponding fieldmap data
				copyFmapData(rawSubDir, oldSubName, bidsSubName, bidsDir, task, "raw", runNum)

				# come up out of the current run directory so you can change into the next one (if there is one)
				os.chdir(taskPath)


	# this section will bidsify the anatomical data and then copy it to every single diretory in the BIDS dir that starts with the specific
	# subject's name/ID

	elif modality == 'T1w':

		### check and see if there have already been BIDS directories created for the subject
		os.chdir(bidsDir)
		subjectDirectories = []

		# look at each of the directories. If they start with the subject's name, add them to the subjectDirectories list
		for directory in os.listdir():
			if directory.startswith(f"sub-{subject}"):
				subjectDirectories.append(directory)
		
		# go into each of these directories and copy over the bidsified anatomical data
		for subDir in subjectDirectories:

			# creat the anatBidsDir for each of the subject's directories and then change into the raw anatomical directory
			anatBidsDir = "".join([bidsDir, "/", subDir, "/anat"])
			try:
				os.makedirs(anatBidsDir)
			except FileExistsError:
				print("")#print("anat bids dir already exists for " + subject)
			anatPath = "".join([rawSubDir, "/anatomy/t1spgr_208sl"])
			if not os.path.isdir(anatPath):
				print(subject + " does not have an anatomy directory.")
				time.sleep(.8)
			else:
				os.chdir(anatPath)

				# create a json file and, if necessary, a nii file for the anatomical data
				# the jsonSubDir is for the sake of the createAndCopyJson function. It's needed so that any files that have 
				# already been generated using dcm2niix with an incorrect BIDS name can be corrected.
				jsonSubDir = "".join([subDir, "_T1w.json"])
				if not createAndCopyJson("", subject, modality, anatBidsDir, jsonSubDir):
					print("json file not available in subject " + subject + "'s anatomy directory... no raw dicoms")
					time.sleep(.8)

				# copy over the nifti anatomical data

				# there's something wrong here. Try to figure out if there just needs to be a generic T1 file that gets copied over and then 
				# renamed accordingly. That might be the way to go regardless.
				try:
					shutil.copy(f"{subDir}_{modality}.nii", anatBidsDir)	
				except:
					os.chdir("dicom")
					dcm2niix("", subDir, modality, "")
					os.chdir("..")
					shutil.copy(f"{subDir}_{modality}.nii", anatBidsDir)



			print(f"successfully bidsified anatomical data for subject {subDir}")
			time.sleep(.8)



# this function copies over the fieldmap data for subject's user selected nifti type and task

def copyFmapData(rawSubDir, oldSubName, bidsSubName, bidsDir, task, niftiFormat, runNum):
	fmapBidsDir = "".join([bidsDir, "/", bidsSubName, "/fmap"])
	try:
		os.makedirs(fmapBidsDir)
	except FileExistsError:
		print(f"field maps already bidsified for {oldSubName} {task} {niftiFormat}")	#print("fmap bids dir already exists for " + subject)
		return
	fmapPath = "".join([rawSubDir, "/func/fieldmaps/FM_", task])
	if not os.path.isdir(fmapPath):
		print("")
	else:
		os.chdir(fmapPath)
		print(f"bidsifying fieldmap data for subject {oldSubName} {task} {niftiFormat}...")

		# create and/or copy the necessary json file over from raw to the fmapBidsDir
		if not createAndCopyJson(task, oldSubName, "epi", fmapBidsDir, bidsSubName):
			print("something goofy happening")
		else:

			### copy the nifti files over to the fmapBIDSDir
			for file in os.listdir():
				if bidsSubName in file:
					shutil.copy(file, fmapBidsDir)
			os.chdir(fmapBidsDir)
			jsonFiles = []
			for file in os.listdir():
				if file.endswith('.json') and task in file:
					jsonFiles.append(file)
			# if the modality is json, things have to be done a bit differently. check series number 
			# if it's greater than 1000, it's AP. If it's less, it's PA. Rename both the json and matching nifti file
			#for i in range(1, fmapNum):
			for idx, json in enumerate(jsonFiles, 1):
				file = open(json)
				data = js.load(file)
				seriesNumber = data["SeriesNumber"]
				matchingNifti = json.replace('.json', '.nii')
				if idx > 1:
					idx -= 1
				if seriesNumber > 1000:
					newFmapNameJson = f"{bidsSubName}{task}run0{idx}_dir-AP_epi.json"
					newFmapNameNifti = f"{bidsSubName}{task}run0{idx}_dir-AP_epi.nii"
					os.rename(json, newFmapNameJson)
					os.rename(matchingNifti, newFmapNameNifti)
				elif seriesNumber < 1000:
					newFmapNameJson = f"{bidsSubName}{task}run0{idx}_dir-PA_epi.json"
					newFmapNameNifti = f"{bidsSubName}{task}run0{idx}_dir-PA_epi.nii"
					os.rename(json, newFmapNameJson)
					os.rename(matchingNifti, newFmapNameNifti)
				idx += 1
			os.chdir(fmapPath)

		#clean up the directory
		os.chdir(fmapBidsDir)
		for file in os.listdir():
			if file.endswith('.nii'):
				continue
			elif file.endswith('.json'):
				continue
			else:
				os.remove(file)
		print(f"Field maps successfully bidsified")
		time.sleep(.8)



# this function serves to get rid of unnecessary underscores and hyphens in the subject's name

def modifySubName(subject):
	if '_' in subject:
		newSubjectName = subject.replace('_', "")
		return newSubjectName
	else:
		return subject
				

# this function needs to go into a specific subject's task directory, and for each run check if a dicom folder exists.
# if it does, make sure a copy of the .json file from the dicom folder gets copied out to the directory above it. If the 
# dicom directory doesn't exist, we will need to untar or unzip the compressed dicom file (check if it exists first. use try and except logic)
# once that is done, we can go into the new dicom directory and run dcm2niix_dev, then copy the json file out when it's done. 
	
def createAndCopyJson(task, subject, modality, jsonDestination, subBidsName):
	# check if dcm2niix_dev has already been run on the subject/task. If it has, copy those files to the subject's BIDS directory
	existingFiles = []
	# change the name to be in json format
	if subBidsName.endswith('.nii'):
		subBidsName = subBidsName.replace('.nii', '.json')

	# look at each of the files in the directory to see if any of them have the specific modality and task in the name and end in '.json'
	# rname the file to be the correct bidsified name
	for file in os.listdir():
		if modality == 'epi':
			if subBidsName in file and file.endswith('.json'):
				#os.rename(file, subBidsName)
				#file = subBidsName
				existingFiles.append(file)
	
		else:
			if file.endswith(f'{modality}.json'):
				os.rename(file, subBidsName)
				file = subBidsName
				existingFiles.append(file)

				
	for file in existingFiles:
		shutil.copy(file, jsonDestination)
	if existingFiles:
		return True
	if not os.path.isdir("dicom"):
		dicomStatus = decompressDicoms(subject)
		if dicomStatus is False:
			return False
	
	os.chdir("dicom")
	print(f"creating json file for {subject} {modality} {task}")
	time.sleep(.8)
	dcm2niix(task, subject, modality, subBidsName)
	os.chdir("..")
	jsonFiles = []
	for file in os.listdir():
		if subBidsName in file and file.endswith('.json'):
			jsonFiles.append(file)
	for json in jsonFiles:
		#if modality == "epi":
		shutil.copy(json, jsonDestination)
	return True


def decompressDicoms(subject):
	dicomFiles = []
	for file in os.listdir():
		if file.startswith('dicom'):
			dicomFiles.append(file)

	if not dicomFiles:
		return False

	print("decompressing dicom files...")

	for dicom in dicomFiles:
		if dicom.endswith(".tgz"):
			untar = "tar -xzf dicom.tgz"
			proc1 = subprocess.Popen(untar, shell=True, stdout=subprocess.PIPE)
			proc1.wait()
			return True
		elif dicom.endswith(".zip"):
			unzip = "unzip dicom.zip"
			proc2 = subprocess.Popen(unzip, shell=True, stdout=subprocess.PIPE)
			proc2.wait()
			return True


def dcm2niix(taskName, subjectName, modality, bidsSubName):
	if modality == "bold" or modality == "epi":
		dcm2niix = f"dcm2niix_dev \
	 					-o ../ \
	 					-x n \
	 					-f {bidsSubName}_task-{taskName}_{modality} \
	 					-z n \
	 					."
		proc1 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		try:
			proc1.communicate()
		except:
			print("dcm2niix picked up an error for subject " + subjectName + " " + taskName + ".\nTry running it manually in the terminal.")
			time.sleep(3)
	elif modality == "T1w":
		dcm2niix = f"dcm2niix_dev \
	 					-o ../ \
	 					-x n \
	 					-f {subjectName}_{modality} \
	 					-z n \
	 					."
		proc2 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		proc2.wait()

def getTotalNumberOfVolumes(subject, file, bidsDir):
	# go to the directory of the recently copied and bidsified data
	# get the number of volumes that the subject currently has via fslinfo, turn it into a json file and then return that number
	os.chdir(bidsDir)
	fslinfo = f'fslinfo {file} > {subject}.txt'
	proc1 = subprocess.Popen(fslinfo, shell=True, stdout=subprocess.PIPE)
	proc1.wait()
	txtFile = f'{subject}.txt'
	dictionary = {}
	with open(txtFile) as f:
		for line in f:
			command, description = line.strip().split(None, 1)
			dictionary[command] = description.strip()
	outJson = open(f'{subject}.json', 'w')
	js.dump(dictionary, outJson, indent = 4, sort_keys = False)
	outJson.close()

	file = open(f"{subject}.json")
	data = js.load(file)
	totalVolumes = data["dim4"]
	totalVolumes = int(totalVolumes)

	# remove unnecessary files
	os.remove(file)
	os.remove(txtFile)

	return totalVolumes


# This function will check if the run_01.nii file for a particular tasks and run have already been copied over to the 
# subject's BIDS directory.

def checkIfCopied(self, task, run, bids_directory):
	os.chdir(bids_directory)
	files = os.listdir()
	for file in files:
		if task in file and run in file and file.endswith(".nii"):
			return True
	return False

# This function renames the copied run_01.nii file to be in BIDS format

def renameFile(self, task, newRun, run, subDir, subName):
	os.chdir(subDir)
	os.rename(f"{run}.nii", f"sub-{subName}" + "_task-" + f"{task}" + f"{newRun}" + "_bold.nii")





