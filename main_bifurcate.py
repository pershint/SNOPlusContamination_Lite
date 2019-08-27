import lib.Bifurcator as bi
import json
import glob
import lib.Bifurcator as bi
import lib.ResultUtils as ru

BIFURDIR = "./data/analysis_data/" #Get all files in this directory
OUTPUTDIR = "./test/"
CONFIGFILE = "./config/config_default.json"

SAVE = True

if __name__=='__main__':
    #Open the configuration JSON as a dictionary
    bifurcation_files = glob.glob(BIFURDIR+"*tuple.root")
    ru.save_bifurcation_list(OUTPUTDIR,bifurcation_files,'bifurcation_analysisfiles.json')
    Bifurcator = bi.Bifurcator(rootfiles=bifurcation_files)
    Bifurcator.load_configdict(CONFIGFILE)
    Bifurcator.Bifurcate()
    Bifurcator.FullBifurcateOutput(outputdir=OUTPUTDIR)
    if SAVE is True:
        Bifurcator.SaveBifurcationSummary(OUTPUTDIR,"bifurcation_boxes.json")
        Bifurcator.SaveBifurcationRoot()
