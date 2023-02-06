# bidsify

This project aims to accept input from a user and then 'bidsify' a neuroimaging dataset
according to their specifications. The bidsify.py script is heavily tailored towards the CPFRC
computing environment at the University of Michigan. bidsconvert.py is much more broadly useable 
across computing environments.

Repository url: https://github.com/danielasay/bidsify

How to use it @ CPFRC:

1. The user needs to download both the bidsify.py and bidsconvert.py files to the lab's remote server and place them in the same directory (exact location doesn't matter)

2. cd into the /PROJECTS/REHARRIS directory and look for the studies.csv file. This file contains some basic information about the different studies and datasets that we have. Take a look at it and make sure that the information for your study of interest is both present and accurate. If not, the bidsify.py script will not function properly.

3. Now that you've verified that the studies.csv file has all the necessary information, you're ready to run bidsify.py. In some cases, the script can take a while to run (e.g. dicom files need to be decompressed). To be safe and protect your data against getting killed halfway through because of a lost connection, you can use Linux Screens. Screens is a way to run commands on a remote server that might take a while by making the commands connection-independent, which is to say that you can start a command on a Screen, sever your ssh connection (or NoMachine session) and the command continues running. You can read about screens here: https://linuxize.com/post/how-to-use-linux-screen/ For our purposes, you really just need to know how to start, exit and resume a screen. 

4. Once you've initialized (or resumed) a screen, navigate to the directory where you placed the bidsconvert.py and bidsify.py files. Execute this command: python3 bidsify.py 

5. The program will start and ask you a series of questions, including which study you want to bidsify, which modalities you want, which nifti files you want, where you want your bidsified data to land, and if you want to remove any volumes from the beginning of your functional data. After you've input all that information, the bidsify work will start. Keep an eye on the messages printed out to the terminal. They will tell you about the progress being made. If anything looks off, kill the program (^c) and investigate the issue. Reach out to Daniel (dasay@med.umich.edu) with any questions or concerns.

A few notes. 

If a study has been previously bidsified, the program will recognize that and notify you. It will check if any new subjects have been added to the raw directory since the last time bidsified was run. You can choose to either re-bidsify the entire dataset, or just bidsify the new subjects and add them to the already created BIDS folder.

If a study has been bidsified on the same day you're trying to bidsify, the program will notify you. This usually happens when the program was killed prematurely and is being re-run. You can either overwrite/redo what's already been done, or delete the BIDS directory labeled with today's date and start over. 

How each function works, starting with bidsconvert.py

1. bidsify(data, bidsDir, niftiFormat, numVolsToChop) is a function that takes four inputs:

data: a list of strings representing the subject, session, modality, sub-path, and task.
bidsDir: a string representing the directory where the BIDS formatted data should be stored.
niftiFormat: a string representing the format of the NIfTI files.
numVolsToChop: an integer representing the number of volumes to chop.
The function starts by extracting the subject, session, modality, sub-path, and task from the data input list. It then prints a message with the extracted information to notify the user. Next, the function calls another function copyData(subject, modality, subPath, task, bidsDir, niftiFormat, numVolsToChop).

In summary, this function is used to organize and format medical imaging data in the Brain Imaging Data Structure (BIDS) format. The input of the function is used to determine the subject, session, modality, sub-path, and task. The function also calls another function copyData() that is responsible for copying and formatting the data.

2. 


dcm2niix(taskName, subjectName, modality) is a function that takes three inputs:

taskName: a string representing the task name.
subjectName: a string representing the subject name.
modality: a string representing the modality (bold, epi or T1w).
The function first checks if the modality input is "bold" or "epi" using an if statement. If it is, the function creates a command dcm2niix_dev -o ../ -x n -f sub-{subjectName}_task-{taskName}_{modality} -z n . to run the "dcm2niix_dev" tool, where {subjectName} and {taskName} are replaced by the corresponding inputs and {modality} is also replaced by the modality input. The command is then executed using the subprocess.Popen() method, and the process is waited for completion.

In case of an error, the function catches the exception and prints a message "dcm2niix_dev picked up an error for subject " + subjectName + " " + taskName + ".\nTry running it manually in the terminal.".

If the modality input is "T1w", the function creates a command dcm2niix_dev -o ../ -x n -f sub-{subjectName}_{modality} -z n . and runs the command in the same way as before.

In summary, this function uses the "dcm2niix_dev" tool to convert DICOM files to NIfTI files. The input of the function is used to determine the format of the command and the output file name. If an error occurs, the function will notify the user with a message.






