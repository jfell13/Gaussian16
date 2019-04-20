#! /usr/bin/env python

##################################
# Create Gaussian 16 input files #
##################################

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
        default='6-31G(d)',
        help='Basis Set (default: 6-31G(d))'
        )
parser.add_argument(
        '-d', metavar='<string>', dest='disp',
        default='',
        help='Additional dispersion correction (Ex: GD2, GD3, GD3BJ; default: none)'
        )
parser.add_argument(
        '-s', metavar='<string>', dest='solv',
        default='',
        help='Additional IEFPCM solvation (Options: water, ethanol, chcl3, or ch2cl2; default: none)'
        )
parser.add_argument(
        '-c', type=int, dest='charge',
        default = '0',
        help = 'Molecular charge (default: 0)'
        )
args = parser.parse_args()

#Dispersion Arguments
if args.disp == 'GD2':
        args.disp = 'EmpiricalDispersion=GD2 '
if args.disp == 'GD3':
        args.disp = 'EmpiricalDispersion=GD3 '
if args.disp == 'GD3BJ':
        args.disp = 'EmpiricalDispersion=GD3BJ '

#Solvation Arguments
if args.solv == 'ethanol':
        args.solv = 'SCRF=(Solvent=Ethanol) '
if args.solv == 'chcl3':
        args.solv = 'SCRF=(Solvent=Chloroform) '
if args.solv == 'ch2cl2':
        args.solv = 'SCRF=(Solvent=Dichloromethane) '
if args.solv == 'water':
        args.solv = 'SCRF=(Solvent=Water) '

# make xyz from pdbs
for i in os.listdir('.'):
        if i[-4:] == '.pdb':
                os.system('/software/openbabel/2.4.0/lssc0-linux/bin/babel -ipdb %s -oxyz %s.xyz' % (i, i[:-4]))
                
# create list of all xyz files in the current directory 
xyz_files = os.listdir(".")
temp_list = xyz_files[:]
for file in temp_list: 
	if not file.endswith(".xyz"): 
		xyz_files.remove(file)
		
# create a Gaussian16 opt file for every xyz file
# remove spaces and parenthesis when necessary
for file in xyz_files:
        g16_filename = file.replace(' ', '')
        g16_filename = g16_filename.replace('(', '')
        g16_filename = g16_filename.replace(')', '')
        print g16_filename
        g16_input = open(g16_filename[:-3]+"com", "w")
        xyz_coordinates = open(file).readlines()
        # write header
        g16_input.write("%chk="+g16_filename[:-4]+".chk\n")
        g16_input.write("#" + args.theory)
        g16_input.write("/" + args.basis)
        g16_input.write(" ")
        g16_input.write(str(args.disp))
        g16_input.write("Opt ")
        g16_input.write(str(args.solv))
        g16_input.write("Freq=NoRaman\n")
        g16_input.write("\n")
        g16_input.write(g16_filename[:-4] + "\n")
        g16_input.write("\n")
        g16_input.write(str(args.charge) + "  1\n")
        # insert coordinates
        for line in xyz_coordinates[2:]:
                g16_input.write(line)
        g16_input.write("\n")
        g16_input.close()
        
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

                        
