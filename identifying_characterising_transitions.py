#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Rachael Armitage

"""

import pandas as pd
from os import listdir
from pyextremes import get_extremes
#import matplotlib.pyplot as plt
#from pyextremes.plotting import plot_extremes

# define models and rcms
models = ['GR4J','GR6J','PDM','G2G'] # models in eflag
rcms = ['RCM1','RCM2','RCM3','RCM4','RCM5','RCM6','RCM7','RCM8','RCM9','RCM10','RCM11','RCM12'] # rcms in eflag

# set thresholds 
# thresholds applied to standardised data to identify transitions between extremes
thresholds = ['Moderate','Severe','Extreme']
Moderate = 1
Severe = 1.6
Extreme = 2

# set paths
inpath = 'input_data/' # location of standardised data directory
outpath_t = 'output_data/' # location to save transitions data to
eflag_metadata_path = 'input_data/eflag_lat_long_69007.csv'


### transition identification and characterisation ###

def extract_transitions(model, rcm, threshold, acc=3):
    """
    Extract and characterise hydrological transitions from the eFLaG dataset
    for a specified hydrological model, regional climate model (RCM), and
    transition threshold.

    Parameters
    ----------
    model : str
        Name of the hydrological model. 
        If using eFLaG, must be one of:
        {'GR4J', 'GR6J', 'PDM', 'G2G'}.

    rcm : str
        Name of the regional climate model simulation. 
        If using eFLaG, must be one of:
        {'RCM1', 'RCM2', 'RCM3', 'RCM4', 'RCM5', 'RCM6',
         'RCM7', 'RCM8', 'RCM9', 'RCM10', 'RCM11', 'RCM12'}.

    threshold : str
        Transition severity threshold. Must be one of:
        {'Moderate', 'Severe', 'Extreme'}, corresponding to absolute
        threshold values of 1.0, 1.6, and 2.0, respectively.
    
    acc : int, default = 3
        Accumulation period of standardised indicator.
        e.g. SSI-3 uses acc=3
        If using eFLaG SSI, must be one of:
        {1, 3, 6, 9, 12, 18, 24}

    Returns
    -------
    csv
        Saves out a csv file containing the extracted transition characteristics
        for the specified model, climate simulation, and threshold.

    """
    
    
    
    
    UseThreshold = threshold

    infold = inpath  + model + '/' + rcm +'/' # path to SSI data for specific model/rcm
                
    StationFiles = [f for f in listdir(infold) if f.endswith('.csv')]
    
    # empty lists for summary data
    MagAvg = []
    DurAvg = []
    InteAvg = []
    StationNo = []
    Frequency = []
    CountSum = []
    
    for f in StationFiles:
        # print statement
        print('processing ' + f + ' from '+ model + ' for ' + UseThreshold)
        
        ### read in SSI data ###
        SSI = pd.read_csv(infold + f)
        #reformat months
        SSI.rename(columns={'Unnamed: 0':'MONTH'}, inplace=True)
        SSI['MONTH'] = pd.to_datetime(SSI['MONTH'])
        SSI = SSI.set_index(['MONTH'])
        # subset accumulation of interest and create pandaseries for next steps
        SSI3 = SSI[f'X{acc}']
            
        
        ### identify individual extreme events ###
        wets = get_extremes(SSI3, 'POT', threshold=eval(UseThreshold))
        drys = get_extremes(SSI3, 'POT', 'low', threshold=-eval(UseThreshold))
        
        # plot extremes 
        # plot_extremes(SSI3, wets, "POT", "high")
        # plot_extremes(SSI3, drys, "POT", "low")
        
        # join wet and dry events
        wets = wets.to_frame()
        wets['EventType'] = 'wet'
        drys = drys.to_frame()
        drys['EventType'] = 'dry'
        events = pd.concat([wets, drys])
        events = events.sort_index()
        

        ### identify transitions from events ###
        # transition period starts at the last extreme of one type and ends at the first following extreme of the opposite
        
        if len(events) > 0:       
            
            transitions = events
            transitions = transitions.reset_index()
            transitions['MONTH'] = transitions['MONTH'].dt.strftime('%b %Y')
            
            StartDates = []
            EndDates = []
            StartState = []
            StartVal = []
            EndVal = []
            
            for i in range(len(transitions['EventType'])-1):
                if transitions['EventType'][i] != transitions['EventType'][i+1]:
                    StartDates.append(transitions['MONTH'][i])
                    EndDates.append(transitions['MONTH'][i+1])
                    StartState.append(transitions['EventType'][i])
                    StartVal.append(transitions[f'X{acc}'][i])
                    EndVal.append(transitions[f'X{acc}'][i+1])
                else:
                    next
                    
            TransitionsData = pd.DataFrame(list(zip(StartDates, EndDates, StartState, StartVal, EndVal)),
                                           columns = ['StartDates', 'EndDates', 'StartState', 'StartVal', 'EndVal'])
            
            TransitionsData['StartDates'] = pd.to_datetime(pd.Series(TransitionsData['StartDates']), format='%b %Y') # may want to change format here
            TransitionsData['EndDates'] = pd.to_datetime(pd.Series(TransitionsData['EndDates']), format='%b %Y')
            
            TransitionsData['StartDates'] = TransitionsData['StartDates'].dt.to_period('M')
            TransitionsData['EndDates'] = TransitionsData['EndDates'].dt.to_period('M')
            
            
            ### transition metrics ###
            # magnitude, duration and intensity of each transition event identified
            
            Magnitude = []
            Duration = []
            Intensity = []
            
            for i in range(len(TransitionsData)):
                # magnitude
                sv = TransitionsData['StartVal'][i]
                ev = TransitionsData['EndVal'][i]
                mag = abs(sv - ev)
                Magnitude.append(mag)
                # duration in months
                sd = TransitionsData['StartDates'][i]
                ed = TransitionsData['EndDates'][i]
                dur = ed - sd
                Duration.append(dur)
             
            TransitionsData['Magnitude'] = Magnitude
            TransitionsData['Duration'] = Duration
            TransitionsData['Duration'] = TransitionsData['Duration'].apply(lambda x: x.n)
            
            for i in range(len(TransitionsData)):
                # intensity
                mag = TransitionsData['Magnitude'][i]
                dur = TransitionsData['Duration'][i]
                inte = mag/dur
                Intensity.append(inte)
            
            TransitionsData['Intensity'] = Intensity
            
            # save transitions
            # csv per catchment for each threshold, model, accumulation, rcm combination
            TransitionsData.to_csv(outpath_t + f'{UseThreshold}/SSI{acc}/Transitions_SSI{acc}_{UseThreshold}_{model}_'+f[20:], index=False)
            
            ### summary transition metrics ###
            # frequency and mean transition magnitude, duration and intensity at each catchment
            
            Count = len(TransitionsData)
            CountSum.append(Count)
            
            # record length (in decades)
            RecordLength = len(SSI3)/120
            
            freq = Count/RecordLength
            Frequency.append(freq)
            
            sMagAvg = TransitionsData['Magnitude'].mean()
            MagAvg.append(sMagAvg)
            
            sDurAvg = TransitionsData['Duration'].mean()
            DurAvg.append(sDurAvg)
            
            sInteAvg = TransitionsData['Intensity'].mean()
            InteAvg.append(sInteAvg)
            
            sn = f[20:]
            sub_list = [rcm, '_', '.csv']
            for sub in sub_list:
                sn = sn.replace(''+sub+'','')
            StationNo.append(sn)
            
        else:
            next
        
    TransitionsSummary = pd.DataFrame(list(zip(StationNo, MagAvg, DurAvg, InteAvg, Frequency, CountSum)),
                                   columns = ['Station','Magnitude', 'Duration', 'Intensity','Frequency', 'Count'])
    
    
    # add station location data 
    StationMeta = pd.read_csv(eflag_metadata_path)
    StationMeta.rename(columns={'ID':'Station'}, inplace=True)
    StationMeta['Station'] = StationMeta['Station'].astype(str)
    StationMeta = StationMeta.set_index(['Station'])
    
    TransitionsSummary = TransitionsSummary.set_index(['Station'])
    
    TS = pd.concat([TransitionsSummary, StationMeta], axis=1, join='inner')
    
    # save summary data with locations
    # csv per accumulation, threshold, model, rcm combination
    TS.to_csv(outpath_t + f'{UseThreshold}/TransitionsSummary_SSI{acc}_{UseThreshold}_{model}_{rcm}.csv')
