#! /usr/bin/env python

# A program to extract energies from Gaussian output. 
# It also replaces the harmonic oscillator approximation by the 
# quasiharmonic approximation used by Truhlar et al. 
# J. Phys. Chem. B, 2011, 115, 14556-14562
# 
# Usage: python g09_quasiharmonic <g09.out> <temperature>

from optparse import OptionParser
import sys
import math


# CONSTANTS
#------------------------------------------------------------------------
GAS_CONSTANT = 8.3144621
PLANCK_CONSTANT = 6.62606957e-34 
BOLTZMANN_CONSTANT = 1.3806488e-23 
SPEED_OF_LIGHT = 2.99792458e10
FREQ_CUTOFF = 100.000
#------------------------------------------------------------------------

# functions
#------------------------------------------------------------------------
def calc_entropy(frequency_wn, temperature):
	"""
	Calculates the entropic contribution (cal/(mol*K)) of a harmonic oscillator for 
	a list of frequencies of vibrational modes
	"""
	entropy = 0
	frequency = [entry * SPEED_OF_LIGHT for entry in frequency_wn]
	for entry in frequency:
		factor = ((PLANCK_CONSTANT*entry)/(BOLTZMANN_CONSTANT*temperature))
		temp = factor*(1/(math.exp(factor)-1)) - math.log(1-math.exp(-factor))
		temp = temp*GAS_CONSTANT/4.184
		entropy = entropy + temp 
	return entropy
#------------------------------------------------------------------------

# some variables
frequencies = []
frequencies_unprojected = []
frequency_wn = []
imaginary = 0
temperature = 298.15

# Read commandline arguments 
g09_output = open(sys.argv[1], 'r')
if len(sys.argv) == 3: 
	temperature = float(sys.argv[2])

# Iterate over output
for line in g09_output:
	# look for low frequencies  
	if line.strip().startswith('Frequencies --'):
		for i in range(2,5):
			x = float(line.strip().split()[i])
			frequencies.append(x)
	# look for unprojected low frequencies 
	if line.strip().startswith('Low frequencies'):
		frequencies_unprojected.extend(line.strip().split()[3:])
	# look if Gaussian finds an imaginary frequency 
	if line.strip().startswith('******    1 imaginary'):
		imaginary = 1
	# look for SCF energies, last one will be correct
	if line.strip().startswith('SCF Done:'):
		scf_energy = float(line.strip().split()[4])
	# look for thermal corrections 
	if line.strip().startswith('Zero-point correction='):
		zero_point_corr = float(line.strip().split()[2]) 
	if line.strip().startswith('Thermal correction to Energy='):
		energy_corr = float(line.strip().split()[4])
	if line.strip().startswith('Thermal correction to Enthalpy='):
		enthalpy_corr = float(line.strip().split()[4]) 
	if line.strip().startswith('Thermal correction to Gibbs Free Energy='):
		gibbs_corr = float(line.strip().split()[6])

# sort out low frequencies 
for entry in frequencies:
	if entry > 0 and entry < FREQ_CUTOFF:
		frequency_wn.append(entry)

# Calculate Truhlar's correction by raising low frequencies to FREQ_CUTOFF
entropy = calc_entropy(frequency_wn, temperature)
correction = (entropy - len(frequency_wn) * calc_entropy([FREQ_CUTOFF], temperature))
# correction in kcal/mol 
correction = (correction * temperature) / 1000
# correction in hartree
correction2 = correction / 627.51
# quasiharmonic free energy correction 
gibbs_corr_quasi = gibbs_corr + correction2

# Calculate energies with thermal corrections 
energy = scf_energy + zero_point_corr
enthalpy = scf_energy + enthalpy_corr
gibbs_energy = scf_energy + gibbs_corr
gibbs_energy_quasi = gibbs_energy + correction2

# OUTPUT 
print "\n There are %i positive frequencies below 100 cm^-1." % len(frequency_wn)
print "\n Zero-point correction:                 %.6f hartree" % zero_point_corr
print " Enthalpy correction:                   %.6f hartree" % enthalpy_corr
print " Free Energy correction:                %.6f hartree" % gibbs_corr
print " Quasiharmonic Free Energy correction:  %.6f hartree" % gibbs_corr_quasi
print "\n SCF Energy:         %.6f hartree" % scf_energy
print " SCF Energy + ZPVE:  %.6f hartree" % energy
print " Enthalpy:           %.6f hartree" % enthalpy
print " Free Energy:        %.6f hartree\n" % gibbs_energy

print " Free Energy with quasiharmonic correction:\
  %.6f hartree  (correction: %.2f kcal/mol)\n" % (gibbs_energy_quasi, correction)

print " -----------------------------------------------"
print " Low frequencies before projection:"
if imaginary:
	print " ", frequencies_unprojected[0]
	print " ", frequencies_unprojected[-2]
	print " ", frequencies_unprojected[-1] + "\n"
else: 
	for x in frequencies_unprojected[-3:]: 
		print " ", x
print " Low frequencies after projection:"
if imaginary:
	for x in frequencies[0:3]:
		print " ", x
else: 
	for x in frequencies[0:3]:
		print " ", x
print " -----------------------------------------------"
print ""










