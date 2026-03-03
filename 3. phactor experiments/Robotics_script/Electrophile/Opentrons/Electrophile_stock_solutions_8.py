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
    
    ["""(2S)-2,3-dihydro-1H-indole-2-carboxylic acid""", """E193""", 486.2862045719189],
    
    ["""1H-indole-3-carboxylic acid""", """E194""", 492.40109208240256],
    
    ["""pyridine-4-carboxylic acid""", """E195""", 484.36901957598894],
    
    ["""2,3-dihydro-1H-indole-2-carboxylic acid""", """E196""", 486.2862045719189],
    
    ["""1H-indazole-3-carboxylic acid""", """E197""", 489.3703361085415],
    
    ["""1H-indole-2-carboxylic acid""", """E198""", 492.40109208240256],
    
    ["""2-methylpropanoic acid""", """E199""", 451.97798206786973],
    
    ["""2-iodobenzoic acid""", """E200""", 533.5790097572776],
    
    ["""2-[4-(2-methylpropyl)phenyl]propanoic acid""", """E201""", 479.77797168896643],
    
    ["""(9Z,12Z)-octadeca-9,12-dienoic acid""", """E202""", 421.960057061341],
    
    ["""(4R)-4-[(3R,5R,8R,9S,10S,13R,14S,17R)-3-hydroxy-10,13-dimethyl-2,3,4,5,6,7,8,9,11,12,14,15,16,17-tetradecahydro-1H-cyclopenta[a]phenanthren-17-yl]pentanoic acid""", """E203""", 416.8539564524694],
    
    ["""1-methylpyrazole-4-carboxylic acid""", """E204""", 630.3668226151772],
    
    ["""2-(3-methoxyphenyl)acetic acid""", """E205""", 620.6650779322381],
    
    ["""2-(4-methylphenyl)propanoic acid""", """E206""", 483.21071863581],
    
    ["""1-methyl-5-thiophen-2-ylpyrazole-3-carboxylic acid""", """E207""", 475.2151363810987],
    
    ["""2-methylpyrazole-3-carboxylic acid""", """E208""", 630.3668226151772],
    
    ["""1-methylpyrazole-3-carboxylic acid""", """E209""", 630.3668226151772],
    
    ["""5-methoxy-1H-indole-3-carboxylic acid""", """E210""", 414.45381316037236],
    
    ["""4-methylsulfonylbenzoic acid""", """E211""", 494.4755506717946],
    
    ["""2-(4-methoxyphenyl)acetic acid""", """E212""", 596.7933441656135],
    
    ["""4-methylsulfanylbenzoic acid""", """E213""", 589.4949765174484],
    
    ["""1-methylpiperidine-3-carboxylic acid""", """E214""", 554.7372538063975],
    
    ["""3-(2-methylphenyl)propanoic acid""", """E215""", 604.0133982947624],
    
    ["""7-methyl-2-propyl-3H-benzimidazole-5-carboxylic acid""", """E216""", 453.1901489117983],
    
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
        

