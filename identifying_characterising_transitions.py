#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Rachael Armitage

"""

import pandas as pd
from pyextremes import get_extremes

# set thresholds 
# thresholds applied to standardised data to identify transitions between extremes
thresholds = ['Moderate','Severe','Extreme']
Moderate = 1
Severe = 1.6
Extreme = 2

# set paths
inpath = 'input_data/' # location of standardised data directory
outpath_t = 'output_data/' # location to save transitions data to

### transition identification and characterisation ###

def extract_transitions(filename, threshold, acc=3):
    """
    Extract and characterise hydrological transitions from the eFLaG dataset
    for a specified hydrological model, regional climate model (RCM), and
    transition threshold.

    Parameters
    ----------
    filename : str
        Name of the csv file that has the standardised indicators.
    
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

    f = inpath + filename # path to SSI/SPI data for specific model/rcm
                
    # empty lists for summary data
    MagAvg = []
    DurAvg = []
    InteAvg = []
    StationNo = []
    Frequency = []
    CountSum = []
    
    print('processing ' + f + ' for ' + UseThreshold)

    ### read in SSI/SPI data ###
    SSI = pd.read_csv(f)
    #reformat months
    SSI.rename(columns={'Unnamed: 0':'MONTH'}, inplace=True)
    SSI['MONTH'] = pd.to_datetime(SSI['MONTH'])
    SSI = SSI.set_index(['MONTH'])
    # subset accumulation of interest and create pandaseries for next steps
    SSI3 = SSI[f'X{acc}']


    ### identify individual extreme events ###
    wets = get_extremes(SSI3, 'POT', threshold=eval(UseThreshold))
    drys = get_extremes(SSI3, 'POT', 'low', threshold=-eval(UseThreshold))

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
        TransitionsData.to_csv(outpath_t + filename[:-4] + '_TransitionsEvents.csv', index=False)

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

    TransitionsSummary = pd.DataFrame(list(zip(MagAvg, DurAvg, InteAvg, Frequency, CountSum)),
                                   columns = ['Magnitude', 'Duration', 'Intensity','Frequency', 'Count'])
    
    # save summary data as a csv file
    TransitionsSummary.to_csv(outpath_t + filename[:-4] + '_TransitionsSummary.csv', index=False)


#Example to run the code
#Please change filename/Threshold/Accumulation as needed
extract_transitions('example_ssi_69007.csv', 'Moderate', acc=3)
