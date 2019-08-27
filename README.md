##SNO+ Contamination study - light edition##

This repository contains scripts and libraries for estimating the instrumental
contamination in SNO+ analysis data using a bifurcated analysis.  The main concepts
behind performing this analysis are discussed in the contamination section of
the SNO+ water unidoc.

Scripts are currently compatible with python 2.7.X.  Upgrading to python3 should
be straightforward.

Dependencies:
  * glob
  * matplotlib
  * pyROOT
  * scipy/numpy

##Description of main scripts and configurables##

The two main scripts are used as follows:

1. main_bifurcate.py: Used to perform the bifurcation analysis on any given
set of SNO+ analysis files in ntuple format.

Description of configurables at the top of the main script:
  - BIFURDIR: Directory where all ntuple files to be bifurcated are stored.
  - OUTPUTDIR: Directory to save all results from the bifurcation analysis.
  - CONFIGFILE: Configuration file in JSON format describing the preliminary
    cuts and bifurcation branch cuts used in the bifurcation analysis.

2. main_contam.py: Used to calculate the instrumental contamination estimate using
results from main_bifurcate.py.  Also requires an estimate of the sacrifice of 
true signal events due to the bifurcation branch cuts (generally estimated using
calibration data).

Description of configurables at the top of the main script:
  - BIFURFILE: Output JSON file from running main_bifurcate.py on analysis ntuple files.
  - SACFILE: Output sacrifice summary from estimating the signal sacrifice due to 
    the bifurcation branch cuts.  Example format can be seen in ./data/tb1/sacrifice_summary.json
  - OUTPUTDIR = Directory to save all results from the contamination estimate calculation.
  - LETACONTAM: Contamination estimate using LETA approximations is calculated.
  - NEGLOGLFIT: Contamination estimate using minimization of log-likelihood function
      assuming Poisson distributions for values measured in a,b,c, and d boxes.
  - BOOTSTRAP: Contamination upper limit estimate by re-shooting values for a,b,c, 
       and d assuming poisson distributions and calculating the contamination 
       estimate.
  - SHOWPLOTS: Show plots from the bootstrap contamination calculation.
  - SAVE: Save outputs from any contamination study run to the output directory.
