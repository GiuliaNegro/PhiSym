#! /bin/bash 
#
# yet another glue script to run phisymmetry calibration
# 
# This one will: 
#    1. Call  makephisym to setup the area
#    2. Use crab to run the calibration step 1
#    3. Run step 2
#
# See usage for instructions
#

crabcfg=phisym-cfg.crab.cfg
crab3cfg=phisym-cfg_crab.py
datadir=$CMSSW_BASE/src/PhiSym/EcalCalibAlgos/data
step2out="CalibHistos.root ehistos.root etsumMean_barl.dat etsumMean_endc.dat PhiSymmetryCalibration_miscal_resid.root PhiSymmetryCalibration.root etsummary_barl.dat etsummary_endc.dat" 

usage(){
    echo "$0 mode dataset globaltag reco nNoise"
    exit
}

#if [ $# -ne 3 ] n° argomenti non equal to 3
if [ $# -ne 5 ]
then
    usage
fi


if [ ! $CRABDIR ] ; then
   echo "Please set CRAB environment"
   exit
fi

dataset=$1
globaltag=$2
mode=$3
reco=$4
nNoise=$5

. phisym-functions.sh

# setup job
echo "$0: Setting up job"
echo "./makephisym2_MC.py --mode=$mode --dataset=$dataset --globaltag=$globaltag --reco=$reco --nNoise=$nNoise" 


./makephisym2_MC.py --mode=$mode --dataset=$dataset --globaltag="$globaltag" --reco=$reco --nNoise=$nNoise

if [ $? -eq 1 ] ; then
   echo "$0 : Got an error from makephisym , exiting" 
   exit 1
fi


#cd into last made dir .. ok think of something smarter
#rundir="$dataset"
#rundir=`echo $rundir | sed s-/-_-g | sed 's/.\(.*\)/\1/'`

#rundir="Neutrino_Pt-2to20_gun_Fall13dr-tsg_PU40bx25_POSTLS162_V2-v1_GEN-SIM-RAW_MultiFit_noise9"
#rundir="Neutrino_Pt-2to20_gun_Fall13dr-tsg_PU40bx25_POSTLS162_V2-v1_GEN-SIM-RAW_MultiFit_noise8"
#rundir="Neutrino_Pt-2to20_gun_Fall13dr-tsg_PU40bx25_POSTLS162_V2-v1_GEN-SIM-RAW_Weights_noise8"
#rundir="Neutrino_Pt-2to20_gun_Fall13dr-tsg_PU40bx25_POSTLS162_V2-v1_GEN-SIM-RAW_Weights_noise9"
#rundir="Neutrino_Pt-2to20_gun_Fall13dr-tsg_PU40bx25_POSTLS162_V2-v1_GEN-SIM-RAW_Weights_noise10"

#rundir='Neutrino_Pt-2to20_gun_Spring14dr-PU20bx50_POSTLS170_V6-v1_GEN-SIM-RAW_Weights_noise10'
#rundir='Neutrino_Pt-2to20_gun_Spring14dr-PU20bx50_POSTLS170_V6-v1_GEN-SIM-RAW_Weights_noise9'
#rundir='Neutrino_Pt-2to20_gun_Spring14dr-PU20bx50_POSTLS170_V6-v1_GEN-SIM-RAW_Weights_noise8'
#rundir='Neutrino_Pt-2to20_gun_Spring14dr-PU20bx50_POSTLS170_V6-v1_GEN-SIM-RAW_MultiFit_noise8'
#rundir='Neutrino_Pt-2to20_gun_Spring14dr-PU20bx50_POSTLS170_V6-v1_GEN-SIM-RAW_MultiFit_noise9'
rundir='Neutrino_Pt-2to20_gun_Spring14dr-PU20bx50_POSTLS170_V6-v1_GEN-SIM-RAW_MultiFit_noise10'

echo "$0 : Running dir is $rundir"
cd  $rundir


# create and submit jobs
echo "$0: Invoking  crab"
if [ "$mode" == "caf" ] || [ "$mode" == "remoteGlidein" ]
then
   source /cvmfs/cms.cern.ch/crab/crab.sh
   crab -cfg $crabcfg -create    
   crab -submit

   findcrabdir

   #keep checking if crab is done
   crabstatus=0  
   while [  $crabstatus -eq 0 ]; do

     sleep 120
     crabdone
   
   done

   crab -getoutput
 
elif [ "$mode" == "crab3" ]
then
   source /cvmfs/cms.cern.ch/crab3/crab.sh
   crab submit $crab3cfg

   findcrabdir

   #keep checking if crab is done
   crabstatus=0  
   while [  $crabstatus -eq 0 ]; do

     sleep 120
     crab3done
   
   done

   crab getoutput 
fi

echo "$0: jobs done,  process step 2"
#crab is done, run step 2

#this is what function dostep2 calls the output dir
i="res"
if [ "$mode" == "crab3" ]
then
  i="results"
fi

dostep2

echo "$0 Done at `date`. Results in $rundir/$i"
