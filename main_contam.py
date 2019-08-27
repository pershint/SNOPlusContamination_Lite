import lib.ContaminationAnalyzer as ca
import json
import matplotlib.pyplot as plt

BIFURFILE = "./data/tb5/bifurcation_boxes.json"
SACFILE = "./data/tb5/sacrifice_summary.json"
OUTPUTDIR = "./"
LETACONTAM = False
NEGLOGLFIT = False
BOOTSTRAP = True

SHOWPLOTS = True
SAVE = True

if __name__=='__main__':
    bifurcation_summary = None
    cut_sac_summary = None
    try:
        with open(BIFURFILE,"r") as f:
            bifurcation_summary = json.load(f)
    except IOError:
        print("Bifurcation Summary loading error.  Was this "+\
                " analysis run?")
        pass
    try:
        with open(SACFILE,"r") as f:
            cut_sac_summary = json.load(f)
    except IOError:
        print("Cut sacrifice Summary loading error.  Was this "+\
                " analysis run?")
        pass

    if LETACONTAM is True:
        print("CALCULATING CONTAMINATION WITH LETA APPROACH")
        CE = ca.LETAContamination(bifurcation_summary,cut_sac_summary)
        contam = CE.CalculateContamination()
        contam_unc = CE.CalculateContaminationUnc()
        print("Estimated contamination: %f"%(contam))
        print("Estimate's uncertainty: %f"%(contam_unc))
        if SAVE is True:
            CE.SaveContaminationSummary(OUTPUTDIR,"contamination_summary_LETA.json")

    if NEGLOGLFIT is True:
        print("FITTING CONTAMINATION PARAMETERS ASSUMING POISSON FLUCTUATIONS")
        CE = ca.LogLikelihoodContam(bifurcation_summary,cut_sac_summary)
        CE.FitContaminationParameters()
        if SAVE is True:
            CE.SaveContaminationSummary(OUTPUTDIR,"contamination_fit_NLL.json")
            CE.SaveMinimizationSummary(OUTPUTDIR,"contamination_fit_MinuitSummary.txt")

    if BOOTSTRAP is True:
        CE = ca.NDContamination(bifurcation_summary,cut_sac_summary)
        CE.CalculateContaminationValues() #Calculate contamination eqns.
        values = CE.BootstrapCL(0.683,100000) #Estimate upper end of y1y2
        if SAVE is True:
            CE.SaveContaminationSummary(OUTPUTDIR,"contamination_summary_bootstrap.json")
        if SHOWPLOTS is True:
            values=values
            plt.hist(values,100,range=(min(values),max(values)))
            plt.xlabel(r"Total estimated contamination (y1y2$\beta$)")
            plt.ylabel(r"Relative probability (unitless)")
            plt.title("Distribution of estimated contamination after\n"+\
                "re-firing variables with statistical uncertainties")
            plt.show()
