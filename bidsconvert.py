#!/usr/bin/python

# This script will go in to each subject's directory and grab the run_01.nii file for each task, copy it over to bacpac_BIDS and then rename it in 
# proper BIDS format


# ideally, this class/library would be able to take a csv file that has all the necessary information to create a BIDS dataset. 


import os
import pprint
import shutil
import sys
import subprocess
import time


BIDS_dir = "/PROJECTS/bacpac/bacpac_BIDS/"
raw_dir = "/PROJECTS/bacpac/raw/"



def bidsify(data, bidsDir, niftiFormat):
	subject = data[0]
	session = data[1]
	modality = data[2]
	subPath = data[3]
	task = data[4]
	print("\nbidsifying data for subject " + subject + " " + modality  + " " + task + ".")
	copyData(subject, modality, subPath, task, bidsDir, niftiFormat)


# I want it take all the info for a given subject, create the BIDS dir if it doesn't already exist,
# then cd into the 'func' dir for bold and 'anat' for T1w, then cd into the task for bold, then iterate
# through each run for that task, copying the desired nii file (run_01.nii, prun_01.nii or from raw) and
# the associated json file to the BIDS directory


# get list of all the subjects in the raw directory

def getSubs(self, raw_directory):
	subs = []
	for dir in os.listdir(raw_dir):
		if dir.startswith("bac"):
			subs.append(dir)
	return subs

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


def copyData(subject, modality, subDir, task, bidsDir, niftiFormat):
	desiredNifti = parseNiftiInfo(niftiFormat)
	if modality == 'bold':
		funcBidsDir = "".join([bidsDir, "/sub-", subject, "/func"])
		try:
			os.makedirs(funcBidsDir)
		except FileExistsError:
			print("")#print("func bids dir already exists for " + subject)
		taskPath = "".join([subDir, "/", "func", "/", task])
		if not os.path.isdir(taskPath):
			print(subject + " does not have a " + task + " directory. Moving to next subject.")
		else:
			os.chdir(taskPath)
			runs = os.listdir()
			for run in runs:
				runNum = run[-2:]
				os.chdir(run)
				if not createAndCopyJson(task, subject, modality, funcBidsDir):
					print("json file not available in subject " + subject + "'s " + task + " directory... no raw dicoms")

				# copy physio corrected run nifti file and bidsify
				if "prun" in niftiFormat:
					newFileName = f"sub-{subject}-prun{runNum}_task-{task}_{modality}.nii"
					if not os.path.exists(f"{funcBidsDir}/{newFileName}"):
						try:
							shutil.copy(f"prun_{runNum}.nii", funcBidsDir)
							newFileName = f"sub-{subject}-prun{runNum}_task-{task}_{modality}.nii"
							os.rename(f"{funcBidsDir}/prun_{runNum}.nii", f"{funcBidsDir}/{newFileName}")
							print("successfully bidsified prun file for subject " + subject)
							time.sleep(.1)
						except FileNotFoundError:
							print("prun file does not exist for subject " + subject + " " + task)
					else:
						print("prun file has already been bidsified for " + subject + " " + task)
				os.chdir("..")

				# copy regular run nifti file and bidsify
				if "regular" in niftiFormat:
					newFileName = f"sub-{subject}-run{runNum}_task-{task}_{modality}.nii"
					if not os.path.exists(f"{funcBidsDir}/{newFileName}"):
						try:
							shutil.copy(f"run_{runNum}.nii", funcBidsDir)
							os.rename(f"{funcBidsDir}/run_{runNum}.nii", f"{funcBidsDir}/{newFileName}")
							print("successfully bidsified regular run file for subject " + subject)
							time.sleep(.1)
						except FileNotFoundError:
							print("regular run file does not exist for subject " + subject + " " + task)
					else:
						print("regular run file has already been bidsified for " + subject + " " + task)

				# copy nifti file converted from raw dicoms and bidsify
				if "raw" in niftiFormat:
					if not os.path.exists(f"{funcBidsDir}/sub-{subject}-raw{runNum}_task-{task}_{modality}.nii"):
						if not createAndCopyJson(task, subject, modality, funcBidsDir):
							print("raw dicoms not available for subject " + subject)
						else:
							try:
								shutil.copy(f"sub-{subject}_task-{task}_{modality}.nii", funcBidsDir)
								os.rename(f"{funcBidsDir}/sub-{subject}_task-{task}_{modality}.nii", f"{funcBidsDir}/sub-{subject}-raw{runNum}_task-{task}_{modality}.nii")
								print("successfully bidsified raw dicom nifti file for subject " + subject)
								time.sleep(.1)
							except FileNotFoundError:
								print("dcm2niix_dev failed for subject " + subject + " " + task + ", which means no raw dicom nifti or json file.\nTry again manually in the terminal.")
								time.sleep(3)
					else:
						print("nifti file converted from raw dicoms has already been bidsified for " + subject + " " + task)


	elif modality == 'T1w':
		anatBidsDir = "".join([bidsDir, "/", subject, "/anat"])
		try:
			os.makedirs(anatBidsDir)
		except FileExistsError:
			print("")#print("anat bids dir already exists for " + subject)
		anatPath = "".join([subDir, "/anatomy/t1spgr_208sl"])
		if not os.path.isdir():
			print(subject + " does not have an anatomy directory.")
		else:
			os.chdir(anatPath)
			if not createAndCopyJson("none", subject, modality, anatBidsDir):
				print("json file not available in subject " + subject + "'s anatomy directory... no raw dicoms")
			shutil.copy(f"sub-{subjectName}_{modality}.nii", anatBidsDir)
				

# this function needs to go into a specific subject's task directory, and for each run check if a dicom folder exists.
# if it does, make sure a copy of the .json file from the dicom folder gets copied out to the directory above it. If the 
# dicom directory doesn't exist, we will need to untar or unzip the compressed dicom file (check if it exists first. use try and except logic)
# once that is done, we can go into the new dicom directory and run dcm2niix_dev, then copy the json file out when it's done. 
	
def createAndCopyJson(task, subject, modality, jsonDestination):
	for file in os.listdir():
		if file.endswith(f'{modality}.json'):
			shutil.copy(file, jsonDestination)
			return True
	if not os.path.isdir("dicom"):
		dicomStatus = decompressDicoms(subject)
		if dicomStatus is False:
			return False
		else:
			os.chdir("dicom")
			print("creating json file for " + subject + modality + task + "...")
			dcm2niix(task, subject, modality)
			os.chdir("..")
			jsonFiles = []
			for file in os.listdir():
				if file.endswith('.json'):
					jsonFiles.append(file)
			for json in jsonFiles:
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
			unzip = "gunzip dicom.zip"
			proc2 = subprocess.Popen(unzip, shell=True, stdout=subprocess.PIPE)
			proc2.wait()
			return True


def dcm2niix(taskName, subjectName, modality):
	if modality == "bold":
		dcm2niix = f"dcm2niix_dev \
	 					-o ../ \
	 					-x n \
	 					-f sub-{subjectName}_task-{taskName}_{modality} \
	 					-z n \
	 					."
		proc1 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		try:
			proc1.wait()
		except:
			print("dcm2niix_dev picked up an error for subject " + subjectName + " " + taskName + ".\nTry running it manually in the terminal.")
	elif modality == "T1w":
		dcm2niix = f"dcm2niix_dev \
	 					-o ../ \
	 					-x n \
	 					-f sub-{subjectName}_{modality} \
	 					-z n \
	 					."
		proc2 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		proc2.wait()


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


#def createAndCopyJson(task, subject, modality, jsonDestination):
#	for file in os.listdir():
#		if file.endswith(f'{modality}.json'):
#			shutil.copy(file, jsonDestination)
#			return True
#	if os.path.isdir("dicom"):
#		os.chdir("dicom")
#		jsonFiles = []
#		for file in os.listdir():
#			if file.endswith('.json'):
#				jsonFiles.append(file)
#		if not jsonFiles:
#			print("creating json file for " + subject + "..." + task)
#			dcm2niix(task, subject, modality)
#			os.chdir("..")
#			for file in os.listdir():
#				if file.endswith('.json'):
#					jsonFiles.append(file)
#			for json in jsonFiles:
#				shutil.copy(json, jsonDestination)
#			print("making it here")
#			return True
#		else:
#			for json in jsonFiles:
#				shutil.copy(json, jsonDestination)
#			return True
#	else:
#		if not decompressDicoms(subject):
#			return False
#		else:
#			createAndCopyJson(task, subject, modality, jsonDestination)




