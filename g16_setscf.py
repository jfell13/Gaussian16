#! /usr/bin/env python

################################################################################
# Extract SCF energies from all Gaussian output files in the current directory # 
################################################################################

import sys
import os
import argparse 

#--------------------------------------------------------------------------------------------------------#
### parse commandline options ###
parser = argparse.ArgumentParser(description='Extract SCF energies from G09 output in this dir')
parser.add_argument(
	'-f', metavar='<string>', dest='filename', 
	default='scf_E.txt', help='filename for storing SCF energies')

args = parser.parse_args()
#--------------------------------------------------------------------------------------------------------#

all_files = os.listdir(".")
g09_files = []
# create list with Gaussian 09 output files
for file in all_files: 
	if file.endswith(".log"): 
		g09_files.append(file)

# open file for writing energies 
output = open(args.filename, "w")

# loop over Gaussian 09 output files and write out energies 
energies = {}
scf_energy = 0
for entry in g09_files: 
	normal_termination = 0
	file = open(entry, "r")
	for line in file: 
		if line.strip().startswith("SCF Done"): 
			scf_energy = float(line.strip().split()[4])
		if line.strip().startswith("Normal termination"):
			normal_termination = 1
	energies[scf_energy] = entry[:-4]
	if not normal_termination: 
		print "Warning: " + entry + " did not terminate properly!"

# sort according to scf energy 
temp = energies.keys()
temp.sort() 

# write to file 
for entry in temp: 
	output.write("%-20s %-18.6f %.2f \n" % (energies[entry], entry, ((entry-temp[0])*627.51) ))





