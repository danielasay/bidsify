# bidsify

This project aims to accept input from a user and then 'bidsify' a neuroimaging dataset
according to their specifications. The bidsify.py script is heavily tailored towards the CPFRC
computing environment at the University of Michigan. bidsconvert.py is much more broadly useable 
across computing environments.

How to use it @ CPFRC:

1. The user needs to download both the bidsify.py and bidsconvert.py files to the lab's remote server and place them in the same directory (exact location doesn't matter)

2. cd into the /PROJECTS/REHARRIS directory and look for the studies.csv file. This file contains some basic information about the different studies and datasets that we have. Take a look at it and make sure that the information for your study of interest is both present and accurate. If not, the bidsify.py script will not function properly.

3. Now that you've verified that the studies.csv file has all the necessary information, you're ready to run bidsify.py. In some cases, the script can take a while to run (e.g. dicom files need to be decompressed). To be safe and protect your data against getting killed halfway through because of a lost connection, you can use Linux Screens. Screens is a way to run commands on a remote server that might take a while by making the commands connection-independent. Which is to say that you can start a command on a Screen, sever your ssh connection (or NoMachine session) and the command continues running. You can read about screens here: https://linuxize.com/post/how-to-use-linux-screen/ For our purposes, you really just need to know how to start, exit and resume a screen. 

4. Once you've initialized (or resumed) a screen, navigate to the directory where you placed the bidsconvert.py and bidsify.py files. Execute this command: python3 bidsify.py 

5. The program will start and ask you a series of questions, including which study you want to bidsify, which modalities you want, which nifti files you want, where you want your bidsified data to land, and if you want to remove any volumes from the beginning of your functional data. After you've input all that information, the bidsify work will start. Keep an eye on the messages printed out to the terminal. They will tell you about the progress being made. If anything looks off, kill the program (^c) and investigate the issue. Reach out to Daniel (dasay@med.umich.edu) with any questions or concerns.

A few notes. 

If a study has been previously bidsified, the program will recognize that and notify you. It will check if any new subjects have been added to the raw directory since the last time bidsified was run. You can choose to either re-bidsify the entire dataset, or just bidsify the new subjects and add them to the already created BIDS folder.

If a study has been bidsified on the same day you're trying to bidsify, the program will notify you. This usually happens when the program was killed prematurely and is being re-run. You can either overwrite/redo what's already been done, or delete the BIDS directory labeled with today's date and start over. 

How it Works:













