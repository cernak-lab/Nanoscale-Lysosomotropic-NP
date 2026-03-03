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
    
    ["""1,2,3,4-TETRAHYDRO-2-NAPHTHOIC ACID, 98%""", """E49""", 562.5046819136256],
    
    ["""3-ACETYLBENZOIC ACID, 98%""", """E50""", 604.1617933723197],
    
    ["""1,4-BENZODIOXANE-6-CARBOXYLIC ACID, 95%""", """E51""", 550.0621669626998],
    
    ["""(R)-1-BOC-NIPECOTIC ACID, 97%""", """E52""", 431.16696471409256],
    
    ["""N-4-BOC-N-1-CBZ-2-PIPERAZINE CARBOXYLIC ACID, 97%""", """E53""", 431.07793633369926],
    
    ["""3-BENZOYLBENZOIC ACID, 98%""", """E54""", 437.0280245767582],
    
    ["""1-BOC-AZETIDINE-3-CARBOXYLIC ACID, 97%""", """E55""", 491.9684921975946],
    
    ["""CIS-3-CARBOMETHOXYCYCLOHEXANE-1-CARBOXYLIC ACID, 97%""", """E56""", 532.0569280343717],
    
    ["""4-CHLOROBENZOIC ACID, 99%""", """E57""", 633.7327542156361],
    
    ["""CYCLOPROPYLACETIC ACID, 98%""", """E58""", 795.0411506192569],
    
    ["""3-CYCLOHEXENE-1-CARBOXYLIC ACID, 98%""", """E59""", 630.1656757827982],
    
    ["""3,4-DICHLOROBENZOIC ACID, 95%""", """E60""", 518.5327993298781],
    
    ["""3-ETHOXYACRYLIC ACID, 95+%""", """E61""", 856.2522607871846],
    
    ["""5-FORMYL-2,4-DIMETHYLPYRROLE-3-CARBOXYLIC ACID, 96%""", """E62""", 593.2292414453218],
    
    ["""5-(FURAN-2-YL)-1,2-OXAZOLE-3-CARBOXYLIC ACID""", """E63""", 553.2537821693742],
    
    ["""2-(FURAN-2-YL)-1,3-THIAZOLE-4-CARBOXYLIC ACID""", """E64""", 811.672131147541],
    
    ["""(S)-(+)-2-PHENYLPROPIONIC ACID, 97%""", """E65""", 872.4037956982086],
    
    ["""METHACRYLIC ACID, 99%""", """E66""", 693.9450574979672],
    
    ["""4-FLUORO-3-HYDROXYBENZOIC ACID, 97%""", """E67""", 635.5739542630196],
    
    ["""2-FLUORO-6-IODOBENZOIC ACID, 97%""", """E68""", 445.11086049396636],
    
    ["""3-FLUOROISONICOTINIC ACID, 98%""", """E69""", 703.7172218284904],
    
    ["""3-FLUORO-2-IODOBENZOIC ACID, 98%""", """E70""", 445.11086049396636],
    
    ["""2-FLUORO-4-(METHYLSULFONYL)BENZOIC ACID, 97+%""", """E71""", 453.295142071494],
    
    ["""2-FLUORO-2-METHYLPROPANOIC ACID, 97%""", """E72""", 1743.7631479736099],
    
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
        
