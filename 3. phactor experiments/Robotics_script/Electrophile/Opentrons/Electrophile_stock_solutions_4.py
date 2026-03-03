#!/usr/bin/env python
# coding: utf-8

# In[6]:


import pandas as pd
import numpy as np
from opentrons import protocol_api
from pandas import DataFrame

metadata = {
    'apiLevel': '2.13',
    'protocolName': '''yu-ting-experiment-Electrophile_stocksolutions''',
    'description': '''yu-ting-experiment-Electrophile_stocksolutions''',
    'author': """ykao"""
    }

data = pd.DataFrame( np.array([
    
    ["""TRANS-4-TERT-BUTYLCYCLOHEXANECARBOXYLIC ACID, 97%""", """E97""", 537.6819341184131],
    
    ["""3-BROMOPROPIONIC ACID, 97%""", """E98""", 648.7229522128522],
    
    ["""5-CHLOROBENZOFURAN-2-CARBOXYLIC ACID, 97%""", """E99""", 503.6987486010783],
    
    ["""N-BUTYRIC ACID, 99+%""", """E100""", 1129.9449551696741],
    
    ["""(-)-CAMPHANIC ACID, 98.0+%""", """E101""", 499.48996064978303],
    
    ["""3-CHLORO-2,2-DIMETHYLPROPIONIC ACID, 97%""", """E102""", 581.7372968223751],
    
    ["""5-CHLORO-2-PYRIDINECARBOXYLIC ACID, 97%""", """E103""", 629.7191367819739],
    
    ["""CITRAZINIC ACID, 97%""", """E104""", 639.7037586229127],
    
    ["""2-(4-CYANOPHENYL)-2,2-DIFLUOROACETIC ACID, 95%""", """E105""", 502.2537283149031],
    
    ["""4-CYANOBENZOIC ACID, 98%""", """E106""", 539.7368313736151],
    
    ["""1-CYCLOHEXENE-1-CARBOXYLIC ACID, 97%""", """E107""", 630.1656757827982],
    
    ["""CROTONIC ACID, 98%""", """E108""", 1249.1011034963408],
    
    ["""(1S)-cyclohex-3-ene-1-carboxylic acid""", """E109""", 630.1656757827982],
    
    ["""2-(DIFLUOROMETHYL)BENZOIC ACID,""", """E110""", 426.207627955615],
    
    ["""2,2-DIFLUORO-2-PHENYLACETIC ACID, 95%""", """E111""", 1174.9507581479113],
    
    ["""DIFLUOROACETIC ACID""", """E112""", 621.8047485160887],
    
    ["""2,2-DIFLUOROPENT-4-ENOIC ACID, 95%""", """E113""", 583.8030859662013],
    
    ["""3,3-DIMETHYLBUTYRIC ACID, 98%""", """E114""", 513.5289256198347],
    
    ["""2,2-DIMETHYL-4-PENTENOIC ACID, 95%""", """E115""", 465.12826714519787],
    
    ["""2,6-DIMETHOXYBENZOIC ACID, 99%""", """E116""", 435.15024427732334],
    
    ["""3,5-DIMETHOXYBENZOIC ACID 99%""", """E117""", 543.9378053466543],
    
    ["""4,5-DIMETHOXY-2-IODOBENZOIC ACID, 98%""", """E118""", 415.4820170740416],
    
    ["""3,4-DIMETHOXYBENZOIC ACID, 99+%""", """E119""", 543.9378053466543],
    
    ["""2-(DIPHENYLPHOSPHINO)BENZOIC ACID, 97%""", """E120""", 417.9205027750571],
    
]),columns=['name','number','volume'])


def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware('opentrons_96_tiprack_300ul', 6) 
    reservoir = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', 3) 
    plate = protocol.load_labware('analytical_24_tuberack_3696.9ul', 2) # previous one analyticalsales_24_tuberack_7400ul
    
    p300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tips]) 
    
    datax = data['volume']
    datax = datax.astype("float").values.tolist()
    location = plate.wells()
    p300.pick_up_tip(tips.wells()[0])
    p300.well_bottom_clearance.aspirate = 5
    p300.well_bottom_clearance.dispense = 15
    for i in range(len(datax)):
        p300.transfer(datax[i], reservoir['A3'], location[i], air_gap = 20, new_tip = 'never')
        



