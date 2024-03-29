import json
import sys
import ROOT
import numpy as np
from numpy import *
import math

#Python Class that takes in a configuration file and a list of root files.
#The bifurcation analysis is run over the files, and a root file is output with
#A "bifurcated" tree.  The tree has all the ntuple information for events that
#Pass the preliminary cuts defined in the config file.

class Bifurcator(object):
    def __init__(self,rootfiles=[]):
        self.rootfile_list = rootfiles
        self.cdict = None
        self.bifurcation_rootfile = None
        self.bifurcation_summary = {}

    def set_savedirectory(self,directory):
        if not os.path.exists(directory):
            os.makedirs(self.save_directory)
        self.save_directory = directory

    def add_rootfile(self, rootfile):
        #Add a rootfile to the list of rootfiles to perform analysis on
        self.rootfile_list.append(rootfile)

    def clear_rootfiles(self):
        self.rootfile_list = []

    def load_configdict(self,config_filepath):
        with open(config_filepath,"r") as f:
            self.cdict = json.load(f)

    def Bifurcate(self):
        self.bifurcation_summary = {}
        #Load all rootfiles into a TChain
        ch = ROOT.TChain("output")
        for f in self.rootfile_list:
            ch.Add(f)
        #Define a list of strings that has all preliminary cuts
        prelimcuts = []
        if self.cdict['r_high'] is not None:
            prelimcuts.append("posr<"+str(self.cdict['r_high']))
        if self.cdict['r_low'] is not None:
            prelimcuts.append("posr>"+str(self.cdict['r_low']))
        if self.cdict['udotr_high'] is not None:
            prelimcuts.append("udotr<"+str(self.cdict['udotr_high']))
        if self.cdict['udotr_low'] is not None:
            prelimcuts.append("udotr>"+str(self.cdict['udotr_low']))
        if self.cdict['E_high'] is not None: 
            prelimcuts.append("energy<"+str(self.cdict['E_high']))
        if self.cdict['E_low'] is not None: 
            prelimcuts.append("energy>"+str(self.cdict['E_low']))
        if self.cdict['Z_low'] is not None:
            prelimcuts.append("posz>"+str(self.cdict['Z_low']*10.0))
        if self.cdict['Z_high'] is not None:
            prelimcuts.append("posz<"+str(self.cdict['Z_high']*10.0))
        prelimcuts.append("fitValid==1")
        prelimcuts.append("((dcFlagged&%s)==%s)" % (self.cdict["path_DCmask"],\
                self.cdict["path_DCmask"]))
        prelimcuts.append("((triggerWord&%s)==0)" % (self.cdict["path_trigmask"]))
        #Define a list of strings with cuts in each bifurcation branch
        cut1list = []
        cut1list.append("((dcFlagged&%s)!=%s)" % (self.cdict["cut1_DCmask"],\
                self.cdict["cut1_DCmask"]))
        cut1list.append("((triggerWord&%s)!=0)" % (self.cdict["cut1_trigmask"]))
        cut2list = []
        cut2list.append("beta14>%s" % (self.cdict["cut2_b14_high"]))
        cut2list.append("beta14<%s" % (self.cdict["cut2_b14_low"]))
        cut2list.append("itr<%s" % (self.cdict["cut2_itr_low"]))
        #For each cut list, fuse it into a single string
        #a,b,c, and d boxes have preliminary cuts + whether or not they
        #pass/fail cut1 and cut2
        prelimbase = self._cutfuse(prelimcuts, "&&")
        abox_cuts = prelimbase + "&&(!(%s))&&(!(%s))" % \
                (self._cutfuse(cut1list,"||"), self._cutfuse(cut2list,"||"))
        bbox_cuts = prelimbase + "&&(!(%s))&&(%s)" % \
                (self._cutfuse(cut1list,"||"), self._cutfuse(cut2list,"||"))
        cbox_cuts = prelimbase + "&&(%s)&&(!(%s))" % \
                (self._cutfuse(cut1list,"||"), self._cutfuse(cut2list,"||"))
        dbox_cuts = prelimbase + "&&(%s)&&(%s)" % \
                (self._cutfuse(cut1list,"||"),self._cutfuse(cut2list,"||"))
        #Use GetEntries with the applied cuts to fill in bifurcation
        #box values
        self.bifurcation_summary["allev"] = ch.GetEntries()
        self.bifurcation_summary["pass_path"] = ch.GetEntries(prelimbase)
        self.bifurcation_summary["a"] = ch.GetEntries(abox_cuts)
        self.bifurcation_summary["b"] = ch.GetEntries(bbox_cuts)
        self.bifurcation_summary["c"] = ch.GetEntries(cbox_cuts)
        self.bifurcation_summary["d"] = ch.GetEntries(dbox_cuts)

    def _cutfuse(self,stringlist,delim):
        outstring = ""
        for j,s in enumerate(stringlist):
            if j == 0:
                outstring = s
            else:
                outstring=outstring+delim+s
        return outstring

    def FullBifurcateOutput(self,outputdir=None):
        '''
        Performs the same bifurcation analysis as the Bifurcate method, but
        saves results into a ROOT file.  The output file produced after running the
        SaveBifurcationRoot method has two trees.  One tree has the a,b,c, and d values
        while the other has all events that pass the preliminary cuts.
        #FIXME: pre-processing is needed to load the posr3 and udotr variables from
        the input ntuple (they don't come in default processed ntuples)
        '''
        if outputdir is None:
            print("Please specify an output directory to save the root file in.")
            return
        self.bifurcation_rootfile = None
        bfile = ROOT.TFile(outputdir+"/bifurcation_result.ntuple.root","CREATE")
        b_root = ROOT.TTree("output","Events involved with bifurcation analysis")
        result = ROOT.TTree("boxes","values for a,b,c, and d boxes")
        #Initialize variables to fill with events passing preliminary cuts
        runID = np.zeros(1,dtype=int)
        #ratversion = np.zeros(1,dtype=str)
        nhits = np.zeros(1,dtype=int)
        nhitsCleaned = np.zeros(1,dtype=int)
        triggerWord = np.zeros(1,dtype=int)
        tubiiWord = np.zeros(1,dtype=int)
        dcApplied = np.zeros(1,dtype=float64)
        dcFlagged = np.zeros(1,dtype=float64)
        uTDays = np.zeros(1,dtype=int)
        uTSecs = np.zeros(1,dtype=int)
        uTNSecs = np.zeros(1,dtype=int)
        fitValid = np.zeros(1,dtype=bool)
        energy = np.zeros(1,dtype=float64)
        itr = np.zeros(1,dtype=float64)
        beta14 = np.zeros(1,dtype=float64)
        posx = np.zeros(1,dtype=float64)
        posy = np.zeros(1,dtype=float64)
        posz = np.zeros(1,dtype=float64)
        dirx = np.zeros(1,dtype=float64)
        diry = np.zeros(1,dtype=float64)
        dirz = np.zeros(1,dtype=float64)
        posr = np.zeros(1,dtype=float64)
        #posr3 = np.zeros(1,dtype=float64)
        #udotr = np.zeros(1,dtype=float64)
        cut1BranchClean = np.zeros(1,dtype=bool)
        cut2BranchClean = np.zeros(1,dtype=bool)

        a = np.zeros(1,dtype=int)
        b = np.zeros(1,dtype=int)
        c = np.zeros(1,dtype=int)
        d = np.zeros(1,dtype=int)


        result.Branch('a', a, 'a/I')
        result.Branch('b', b, 'b/I')
        result.Branch('c', c, 'c/I')
        result.Branch('d', d, 'd/I')

        #Now, associate initialized variables with the TTree
        b_root.Branch('runID',runID, 'runID/I')
        #b_root.Branch('ratversion',ratversion, 'ratversion/C')
        b_root.Branch('nhits',nhits, 'nhits/I')
        b_root.Branch('nhitsCleaned',nhitsCleaned, 'nhitsCleaned/I')
        b_root.Branch('triggerWord', triggerWord, 'triggerWord/I')
        b_root.Branch('tubiiWord', tubiiWord, 'tubiiWord/I')
        b_root.Branch('dcApplied', dcApplied, 'dcApplied/D')
        b_root.Branch('dcFlagged', dcFlagged, 'dcFlagged/D')
        b_root.Branch('uTDays',uTDays, 'uTDays/I')
        b_root.Branch('uTSecs',uTSecs, 'uTSecs/I')
        b_root.Branch('uTNSecs',uTNSecs, 'uTNSecs/I')
        b_root.Branch('fitValid',fitValid, 'fitValid/O')
        b_root.Branch('energy',energy, 'energy/D')
        b_root.Branch('itr', itr, 'itr/D')
        b_root.Branch('posx',posx, 'posx/D')
        b_root.Branch('posy',posy, 'posy/D')
        b_root.Branch('posz',posz, 'posz/D')
        b_root.Branch('dirx',dirx, 'dirx/D')
        b_root.Branch('diry',diry, 'diry/D')
        b_root.Branch('dirz',dirz, 'dirz/D')
        b_root.Branch('posr',posr, 'posr/D')
        #b_root.Branch('posr3',posr3, 'posr3/D')
        #b_root.Branch('udotr', udotr, 'udotr/D')
        b_root.Branch('beta14', beta14, 'beta14/D')
        b_root.Branch('cut1BranchClean',cut1BranchClean, 'cut1BranchClean/O')
        b_root.Branch('cut2BranchClean',cut2BranchClean, 'cut2BranchClean/O')

        a[0],b[0],c[0],d[0] = 0,0,0,0
        prelimcuts = []
        if self.cdict['r_high'] is not None:
            prelimcuts.append("posr<"+str(self.cdict['r_high']))
        if self.cdict['r_low'] is not None:
            prelimcuts.append("posr>"+str(self.cdict['r_low']))
        if self.cdict['udotr_high'] is not None:
            prelimcuts.append("udotr<"+str(self.cdict['udotr_high']))
        if self.cdict['udotr_low'] is not None:
            prelimcuts.append("udotr>"+str(self.cdict['udotr_low']))
        if self.cdict['E_high'] is not None: 
            prelimcuts.append("energy<"+str(self.cdict['E_high']))
        if self.cdict['E_low'] is not None: 
            prelimcuts.append("energy>"+str(self.cdict['E_low']))
        if self.cdict['Z_low'] is not None:
            prelimcuts.append("posz>"+str(self.cdict['Z_low']*10.0))
        if self.cdict['Z_high'] is not None:
            prelimcuts.append("posz<"+str(self.cdict['Z_high']*10.0))
        prelimcuts.append("fitValid==1")
        prelimcuts.append("((dcFlagged&%s)==%s)" % (self.cdict["path_DCmask"],\
                self.cdict["path_DCmask"]))
        prelimcuts.append("((triggerWord&%s)==0)" % (self.cdict["path_trigmask"]))
        cut1list = []
        cut1list.append("((dcFlagged&%s)!=%s)" % (self.cdict["cut1_DCmask"],\
                self.cdict["cut1_DCmask"]))
        cut1list.append("((triggerWord&%s)!=0)" % (self.cdict["cut1_trigmask"]))
        cut2list = []
        cut2list.append("beta14>%s" % (self.cdict["cut2_b14_high"]))
        cut2list.append("beta14<%s" % (self.cdict["cut2_b14_low"]))
        cut2list.append("itr<%s" % (self.cdict["cut2_itr_low"]))
        prelimbase = self._cutfuse(prelimcuts, "&&")
       
        for rf in self.rootfile_list:
            rootfile=ROOT.TFile(rf,"READ")
            rootfile.cd()
            datatree=rootfile.Get("output")
            #We define a formula for the preliminary cuts, as
            #well as for each of the bifurcation boxes
            prelimcut = ROOT.TTreeFormula("prelimbase_cut",prelimbase,datatree)
            abox_cuts = prelimbase + "&&(!(%s))&&(!(%s))" % \
                    (self._cutfuse(cut1list,"||"), self._cutfuse(cut2list,"||"))
            bbox_cuts = prelimbase + "&&(!(%s))&&(%s)" % \
                    (self._cutfuse(cut1list,"||"), self._cutfuse(cut2list,"||"))
            cbox_cuts = prelimbase + "&&(%s)&&(!(%s))" % \
                    (self._cutfuse(cut1list,"||"), self._cutfuse(cut2list,"||"))
            dbox_cuts = prelimbase + "&&(%s)&&(%s)" % \
                    (self._cutfuse(cut1list,"||"),self._cutfuse(cut2list,"||"))
            acut = ROOT.TTreeFormula("abox_cut",abox_cuts,datatree)
            bcut = ROOT.TTreeFormula("bbox_cut",bbox_cuts,datatree)
            ccut = ROOT.TTreeFormula("cbox_cut",cbox_cuts,datatree)
            dcut = ROOT.TTreeFormula("dbox_cut",dbox_cuts,datatree)
            for i in xrange(datatree.GetEntries()):
                datatree.GetEntry(i)
                #If this event fails the base cuts, continue
                if not prelimcut.EvalInstance():
                    continue
                if acut.EvalInstance():
                    a[0]+=1
                    cut1_clean = True
                    cut2_clean = True
                if bcut.EvalInstance():
                    cut1_clean = True
                    cut2_clean = False
                    b[0]+=1
                if ccut.EvalInstance():
                    cut1_clean = False
                    cut2_clean = True 
                    c[0]+=1
                elif dcut.EvalInstance():
                    cut1_clean = False
                    cut2_clean = False
                    d[0]+=1
                runID[0] = datatree.runID
                #ratversion[0] = ch.ratversion
                nhits[0] = datatree.nhits
                nhitsCleaned[0] = datatree.nhitsCleaned
                triggerWord[0] = datatree.triggerWord
                tubiiWord[0] = datatree.tubiiWord
                dcApplied[0] = datatree.dcApplied
                dcFlagged[0] = datatree.dcFlagged
                uTDays[0] = datatree.uTDays
                uTSecs[0] = datatree.uTSecs
                uTNSecs[0] = datatree.uTNSecs
                fitValid[0] = datatree.fitValid
                energy[0] = datatree.energy
                itr[0] = datatree.itr
                beta14[0] = datatree.beta14
                posx[0] = datatree.posx
                posy[0] = datatree.posy
                posz[0] = datatree.posz
                dirx[0] = datatree.dirx
                diry[0] = datatree.diry
                dirz[0] = datatree.dirz
                posr[0] = datatree.posr
                #posr3[0] = datatree.posr3
                #udotr[0] = datatree.udotr
                cut1BranchClean[0] = cut1_clean
                cut2BranchClean[0] = cut2_clean
                b_root.Fill()
        result.Fill() #saves a, b, c, and d
        bfile.cd()
        b_root.Write()
        result.Write()
        self.bifurcation_rootfile = bfile

    def SaveBifurcationSummary(self,savedir,savename):
        savesacloc = savedir+"/"+savename
        with open(savesacloc,"w") as f:
            json.dump(self.bifurcation_summary, f, sort_keys=True,indent=4)

    def LoadBifurcationSummary(self,loaddir,filename):
        loadsacloc = loaddir+"/"+filename
        with open(loadsacloc,"w") as f:
            self.bifurcation_summary = json.load(f)
            
    def SaveBifurcationRoot(self):
        self.bifurcation_rootfile.Write()
        self.bifurcation_rootfile.Close()

