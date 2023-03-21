#!/usr/bin/python

### This script is meant to serve as a way for users to run a commmand from the command line and have the data come out in BIDS format. 

# This is a simple script. The ideal use case would be creating a bash alias that calls this script while in a directory of raw dicoms. 
## This script is mostly a simplified version of bidsify.py and bidsconvert.py

import subprocess
import time
import os
import pprint
import shutil
import socket
import json as js

# This function will take the dicoms in the current working directory and convert them to nii and BIDS format. 


#find out if working on the old or new server

def getHostname():
	hostname = socket.gethostname()
	return hostname


def dcm2niix_dev(taskName, subjectName, modality, hostname):
	# if it's a functional bold run

	# use dcm2niix if on new server

	if modality == "bold":
		dcm2niix = f"dcm2niix_dev \
	 					-o . \
	 					-x n \
	 					-f sub-{subjectName}_task-{taskName}_{modality} \
	 					-z n \
	 					."
		proc1 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		try:
			print("Running dcm2niix_dev...")
			proc1.communicate()
		except:
			print("dcm2niix_dev picked up an error for subject " + subjectName + " " + taskName + ".\nTry running it manually in the terminal.")
			time.sleep(10)	
	# if it's a fieldmap run	
	elif modality == 'epi':
		dcm2niix = f"dcm2niix_dev \
	 					-o . \
	 					-x n \
	 					-f sub-{subjectName}_{modality} \
	 					-z n \
	 					."
		proc2 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		print("Running dcm2niix_dev...")
		proc2.communicate()
		jsonFiles = []
		for file in os.listdir():
			if file.endswith('.json'):
				jsonFiles.append(file)
		for json in jsonFiles:
			file = open(json)
			data = js.load(file)
			seriesNumber = data["SeriesNumber"]
			matchingNifti = json.replace('.json', '.nii')
			# check if the json file series number is greater or less than 1000 to determine phase encode direction
			if seriesNumber > 1000:
				newFmapNameJson = f"sub-{subjectName}_task-{task}_dir-AP_epi.json"
				newFmapNameNifti = f"sub-{subjectName}_task-{task}_dir-AP_epi.nii"
				os.rename(json, newFmapNameJson)
				os.rename(matchingNifti, newFmapNameNifti)
			elif seriesNumber < 1000:
				newFmapNameJson = f"sub-{subjectName}_task-{task}_dir-PA_epi.json"
				newFmapNameNifti = f"sub-{subjectName}_task-{task}_dir-PA_epi.nii"
				os.rename(json, newFmapNameJson)
				os.rename(matchingNifti, newFmapNameNifti)
	# if it's an anatomical run	
	elif modality == "T1w":
		dcm2niix = f"dcm2niix_dev \
	 					-o . \
	 					-x n \
	 					-f sub-{subjectName}_{modality} \
	 					-z n \
	 					."
		proc3 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		print("Running dcm2niix_dev...")
		proc3.communicate()

# function to run the non-dev version of dcm2niix

def dcm2niix(taskName, subjectName, modality, hostname):
	# if it's a functional bold run

	# use dcm2niix if on new server

	if modality == "bold":
		dcm2niix = f"dcm2niix \
	 					-o . \
	 					-x n \
	 					-f sub-{subjectName}_task-{taskName}_{modality} \
	 					-z n \
	 					."
		proc1 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		try:
			print("Running dcm2niix...")
			proc1.communicate()
		except:
			print("dcm2niix_dev picked up an error for subject " + subjectName + " " + taskName + ".\nTry running it manually in the terminal.")
			time.sleep(10)	
	# if it's a fieldmap run	
	elif modality == 'epi':
		dcm2niix = f"dcm2niix \
	 					-o . \
	 					-x n \
	 					-f sub-{subjectName}_{modality} \
	 					-z n \
	 					."
		proc2 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		print("Running dcm2niix...")
		proc2.communicate()
		jsonFiles = []
		for file in os.listdir():
			if file.endswith('.json'):
				jsonFiles.append(file)
		for json in jsonFiles:
			file = open(json)
			data = js.load(file)
			seriesNumber = data["SeriesNumber"]
			matchingNifti = json.replace('.json', '.nii')
			# check if the json file series number is greater or less than 1000 to determine phase encode direction
			if seriesNumber > 1000:
				newFmapNameJson = f"sub-{subjectName}_task-{task}_dir-AP_epi.json"
				newFmapNameNifti = f"sub-{subjectName}_task-{task}_dir-AP_epi.nii"
				os.rename(json, newFmapNameJson)
				os.rename(matchingNifti, newFmapNameNifti)
			elif seriesNumber < 1000:
				newFmapNameJson = f"sub-{subjectName}_task-{task}_dir-PA_epi.json"
				newFmapNameNifti = f"sub-{subjectName}_task-{task}_dir-PA_epi.nii"
				os.rename(json, newFmapNameJson)
				os.rename(matchingNifti, newFmapNameNifti)
	# if it's an anatomical run	
	elif modality == "T1w":
		dcm2niix = f"dcm2niix \
	 					-o . \
	 					-x n \
	 					-f sub-{subjectName}_{modality} \
	 					-z n \
	 					."
		proc3 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		print("Running dcm2niix...")
		proc3.communicate()


# printing out the current working directory may help the user when asked for the task name, subject name and modality. 

print("Print out the current working directory for user reference:")

print(os.getcwd())

print('')

# ask for relevant information from the user

task = input('Enter the task name: ')

subjectName = input('Enter the subject name: ')

modality = input('Enter the modality: ')

# get the current hostname (are you on old or new server)

hostname = getHostname()

# run dcm2niix with the given parameters

dcm2niix_dev(task, subjectName, modality, hostname)


# create a list of the output and print to terminal

output = []

for file in os.listdir():
	if file.startswith("sub-"):
		output.append(file)

# if the output array is empty, run dcm2niix non-dev version

if not output:
	print("dcm2niix_dev didn't yield any output. Trying non-dev dcm2niix.")
	dcm2niix(task, subjectName, modality, hostname)
	for file in os.listdir():
		if file.startswith("sub-"):
			output.append(file)

print('')

print(f'Output: {output}')

# this asks the user for the path they would like to copy the data to (if applicable)

print('')

bidsPath = input("Enter the path where you want the output copied to: ")

print('')


for file in output:
	print(f'Copying {file} to {bidsPath}...')
	shutil.copy(file, bidsPath)

print("Done!")








