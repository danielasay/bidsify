#!/usr/bin/python

### This script is meant to serve as a way for users to run a commmand from the command line and have the data come out in BIDS format. 

# This is a simple script. The ideal use case would be creating a bash alias that calls this script while in a directory of raw dicoms. 
## This script is mostly a simplified version of bidsify.py and bidsconvert.py

import subprocess
import time
import os
import pprint
import shutil

# This function will take the dicoms in the current working directory and convert them to nii and BIDS format. 

def dcm2niix(taskName, subjectName, modality):
	if modality == "bold" or modality == "epi":
		dcm2niix = f"dcm2niix \
	 					-o . \
	 					-x n \
	 					-f sub-{subjectName}_task-{taskName}_{modality} \
	 					-z n \
	 					."
		proc1 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		try:
			print("Running dcm2niix...")
			proc1.wait()
		except:
			print("dcm2niix_dev picked up an error for subject " + subjectName + " " + taskName + ".\nTry running it manually in the terminal.")
			time.sleep(10)
	elif modality == "T1w":
		dcm2niix = f"dcm2niix \
	 					-o . \
	 					-x n \
	 					-f sub-{subjectName}_{modality} \
	 					-z n \
	 					."
		proc2 = subprocess.Popen(dcm2niix, shell=True, stdout=subprocess.PIPE)
		print("Running dcm2niix...")
		proc2.wait()


# printing out the current working directory may help the user when asked for the task name, subject name and modality. 

print("Print out the current working directory for user reference:")

print(os.getcwd())

print('')

# ask for relevant information from the user

task = input('Enter the task name: ')

subjectName = input('Enter the subject name: ')

modality = input('Enter the modality: ')

# run dcm2niix with the given parameters

dcm2niix(task, subjectName, modality)


# create a list of the output and print to terminal

output = []

for file in os.listdir():
	if file.endswith("nii") or file.endswith('json'):
		output.append(file)

print('')

print(f'Output: {output}')

# this asks the user for the path they would like to copy the data to (if applicable)

print('')

bidsPath = input("Enter the path where you want the output copied to: ")


for file in output:
	print(f'Copying {file} to {bidsPath}...')
	shutil.copy(file, bidsPath)

print("Done!")








