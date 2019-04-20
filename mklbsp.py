#! /usr/bin/env python

#################################################
# Create Gaussian16 LBSP files from Gaissuain16 #
# optimizations                                 #
#################################################

import sys
import os
import argparse 


# parse commandline options 
parser = argparse.ArgumentParser(description='Create Gaussian16 LBSP file from chk files')
parser.add_argument(
	'-t', metavar='<string>', dest='theory', 
	default='B3LYP', 
	help='Theory to use (default: B3LYP)'
	)
parser.add_argument(
	'-b', metavar='<string>', dest='basis', 
	default='6-311+G(d,p)', 
	help='Basis Set (default: 6-311+G(d,p))'
	)
parser.add_argument(
        '-d', metavar='<string>', dest='disp',
        choices=['none', 'GD2', 'GD3'],
        default='EmpiricalDispersion=GD3BJ ',
        help='Additional dispersion correction (Options: none, GD2, or GD3; default: GD3BJ)'
        )
parser.add_argument(
        '-s', metavar='<string>', dest='solv',
        choices=['none','ethanol','chcl3','ch2cl2'],
        default='SCRF=(Solvent=Water) ',
        help='Additional IEFPCM solvation (Options: none, ethanol, chcl3, or ch2cl2; default: Water)'
        )

args = parser.parse_args()

#Dispersion Arguments
if args.disp == 'GD2':
        args.disp = 'EmpiricalDispersion=GD2 '
if args.disp == 'GD3':
        args.disp = 'EmpiricalDispersion=GD3 '
if args.disp == 'none':
        args.disp = ' '

#Solvation Arguments
if args.solv == 'ethanol':
        args.solv = 'SCRF=(Solvent=Ethanol) '
if args.solv == 'chcl3':
        args.solv = 'SCRF=(Solvent=Chloroform) '
if args.solv == 'ch2cl2':
        args.solv = 'SCRF=(Solvent=Dichloromethane) '
if args.solv == 'none':
        args.solv = ' '
        
# create list of all chk files in the current directory 
chk_files = os.listdir(".")
temp_list = chk_files[:]
for file in temp_list: 
	if not file.endswith("opt.chk"): 
		chk_files.remove(file)
		
# create a Gaussian16 LBSP file for every chk file 
# remove spaces and parenthesis when necessary 
for file in chk_files:
	g16_filename = file.replace(' ', '') 
	g16_filename = g16_filename.replace('(', '') 
	g16_filename = g16_filename.replace(')', '')
        g16_filename = g16_filename.replace('opt', 'lbsp')
	print g16_filename 
	g16_input = open(g16_filename[:-3]+"com", "w")
	# write header 	
	g16_input.write("%chk="+g16_filename[:-4]+".chk\n")
	g16_input.write("#" + args.theory)
        g16_input.write("/" + args.basis)
        g16_input.write(" Guess=Read Geom=Checkpoint ")
        g16_input.write(args.disp)
        g16_input.write(args.solv + "\n")
	g16_input.write("\n")
	g16_input.write(g16_filename[:-4] + "\n")
	g16_input.write("\n")
	g16_input.write("0  1\n")
	g16_input.write("\n")
	g16_input.close() 
        # Copy opt.chk to lbsp.chk        
        os.system('cp %s %s' % (file, g16_filename))
        
# To also create submission files for Barbera#
for i in os.listdir('.'):
        if i[-4:] == '.com':
                name = i[:-4]
                with open('%s.sh' % (name), 'w') as sub_f:
                        sub_f.write('#!/bin/bash\n')
                        sub_f.write('#SBATCH --job-name=%s\n' % (i[:8]))
                        sub_f.write('#SBATCH --output=%s.log\n' % (name))
                        sub_f.write('#SBATCH --error=%s.err\n' % (name))
                        sub_f.write('#SBATCH --mem-per-cpu=20G\n')
                        sub_f.write('#SBATCH --nodes=1\n')
                        sub_f.write('#SBATCH --time=1-0\n')
                        sub_f.write('#SBATCH --mail-user=jsfell@ucdavis.edu\n')
                        sub_f.write('#SBATCH --mail-type=ALL\n')
                        sub_f.write('#SBATCH --partition=production\n\n')
                        sub_f.write('module load gaussian\n')
                        sub_f.write('source $g16root/g16/bsd/g16.profile\n')
                        sub_f.write('g16 %s\n' % (i))
                        sub_f.close()
