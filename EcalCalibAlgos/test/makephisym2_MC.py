#!/usr/bin/env python

#
# Prepare configuration for a phi symmetry calibration
#
# Author: Stefano Argiro
#
#
# Usage:
#
# makephisym.py --mode=[caf|grid] --dataset=[datasetname]
#               --runrange=[first-last] --globaltag=[tag]
#
#
#
# Files: phisym-cfg.py.tmpl phisym-crab-cfg.tmpl 
#

import string, sys, os, getopt, subprocess, time, shutil



def usage():
    print "Usage: makephisym2_MC.py --mode=[caf|grid|crab3] --dataset=[datasetname]"
    print "       --globaltag=[tag] --reco=[recoMethod] --nNoise=[noiseNumber] [--step2only]"     #reco=MultiFit/Weights, nNoise=8/9/10
    
try:
     opts, args = getopt.getopt(sys.argv[1:], "m:d:g:r:n:s", ["mode=","dataset=","globaltag=","reco=","nNoise=","step2only"])

except getopt.GetoptError:
     #* print help information and exit:*
     usage()
     sys.exit(2)


mode=''
dataset=''
globaltag=''
reco=''
nNoise=''
step2only=0

cmssw_py_template=   'phisym-cfg.py.tmpl'
cmssw_py_step2_template= 'phisym_step2.py.tmpl'
runreg_cfg_template= 'runreg.cfg.tmpl'


for opt, arg in opts:
    
     if opt in ("-m", "--mode"):
        mode = arg
        if mode != 'caf' and mode != 'remoteGlidein'  and mode != 'crab3' :
           print sys.argv[0]+" mode must be caf, glite or crab3"
           sys.exit(2)

        if mode == 'crab3':
           crab_cfg_template=   'phisym-cfg.crab3.tmpl'
        else:
           crab_cfg_template=   'phisym-cfg.crab.tmpl'
            
     if opt in ("-d","--dataset"):
      dataset= arg        
            
     if opt in ("-g","--globaltag"):
         globaltag=arg

     if opt in ("-r","--reco"):
      reco=arg

     if opt in ("-n","--nNoise"):
      nNoise=arg

     if opt in ("-s","--step2only"):
         step2only=1


if dataset=='':
    usage()
    print "Please specify dataset"
    sys.exit(2)

if mode=='':    
    usage()
    print "Please specify mode caf, glite or crab3"
    sys.exit(2)

if reco=='':
    usage()
    print "Please specify reco"
    sys.exit(2)

if nNoise=='':
    usage()
    print "Please specify nNoise"
    sys.exit(2)

        
print "Querying DBS ..."

#query='dbs search --url=\"http://cmsdbsprod.cern.ch/cms_dbs_prod_global/servlet/DBSServlet\" --query=\"find file where dataset = '+dataset+' and run ='+repr(firstrun)+'\"'
query = '$PWD/das_client.py --query=\"file dataset='+dataset+'\"'

queryp=subprocess.Popen(query,stdout=subprocess.PIPE,shell=True)
queryp.wait()
res=queryp.stdout
lines=res.readlines()
step2file=lines[len(lines)-1]
step2file=step2file[:len(step2file)-1] # this ugly trick to remove trailing /n

if step2file.find(".root") is -1 :
    print "Error, dbs search gave no files"
    sys.exit(1)

f = open(crab_cfg_template)
data=f.read()
data=data.replace('MODE',mode)
data=data.replace('DATASET',dataset)
if mode == 'crab3':
   data=data.replace('LUMIMASK','')
   outfile = open('phisym-cfg_crab.py',"w")
   outfile.write(data)
   outfile.close()
else:
   data=data.replace('LUMIMASK','#lumi_mask=jsonls-alcaphisym.txt')
   data=data.replace('TOTALNUMBERLUMIS','#total_number_of_lumis = -1')
   data=data.replace('LUMISPERJOB','#lumis_per_job = 100')
   outfile = open('phisym-cfg.crab.cfg',"w")
   outfile.write(data)
   outfile.close()

f = open(cmssw_py_step2_template)
data=f.read()
data=data.replace('GLOBALTAG',globaltag)
data=data.replace('STEP2FILES','/store/data/Run2012D/AlCaPhiSym/RAW/v1/000/208/840/7ED7D113-7A43-E211-BD93-001D09F24D8A.root')
outfile = open('phisym_step2.py',"w")
outfile.write(data)
outfile.close()


f = open(cmssw_py_template)
data=f.read()
data=data.replace('RAWTODIGI','RawToDigi_cff')
data=data.replace('GLOBALTAG',globaltag)
outfile = open('phisym-cfg.py',"w")
outfile.write(data)
outfile.close()

friendly_datasetname=dataset.replace('/','_')+'_'+reco+'_noise'+nNoise
dirname=friendly_datasetname[1:]

if not step2only:
   try :
      os.mkdir(dirname)
   except Exception:
      print "Error creating work directory" 
      sys.exit(1)

else:
   if not os.path.exists(dirname):
       print "Dir not found: ",dirname
       print "It appears step1 was not run"
       sys.exit(1)
       
if not step2only:   
   shutil.move('phisym-cfg.py',dirname)
   if mode == 'crab3': 
      shutil.move('phisym-cfg_crab.py',dirname)
   else:
      shutil.move('phisym-cfg.crab.cfg',dirname)

os.rename('phisym_step2.py',dirname+'/phisym_step2.py')
