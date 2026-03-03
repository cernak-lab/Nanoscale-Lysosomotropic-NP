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
    
    ["""3-(4-Bromophenyl)acrylic acid""", """E289""", 435.4316229905307],
    
    ["""CYCLOPROPANECARBOXYLIC ACID, 95%""", """E290""", 693.9450574979672],
    
    ["""4-(Trifluoromethyl)benzoic acid""", """E291""", 520.9835893120134],
    
    ["""3-quinolinecarboxylic acid""", """E292""", 572.4672287347693],
    
    ["""M-TOLUIC ACID, 99%""", """E293""", 817.0221079691515],
    
    ["""6-Quinolinecarboxylic Acid""", """E294""", 572.4672287347693],
    
    ["""6-phenoxyhexanoic acid""", """E295""", 475.1920768307323],
    
    ["""2-Methoxybenzoic acid""", """E296""", 521.7969109431482],
    
    ["""Flumequine""", """E297""", 415.55263157894734],
    
    ["""Methoxy-1-methyl-1H-pyrazole-5-carboxylic acid""", """E298""", 508.3607019341616],
    
    ["""Methoxyphenyl)propiolic acid""", """E299""", 438.8541579156497],
    
    ["""Trifluoromethyl)phenylacetic acid""", """E300""", 484.8359049718344],
    
    ["""Urocanic acid""", """E301""", 575.2064871126556],
    
    ["""3-(2-Naphthyl)propanoic Acid""", """E302""", 494.42566049043603],
    
    ["""3-(Naphthalen-2-yl)acrylic acid""", """E303""", 499.48996064978303],
    
    ["""3-(Naphthalen-1-yl)acrylic acid""", """E304""", 499.48996064978303],
    
    ["""2-(2-(2-Methoxyethoxy)ethoxy)acetic acid""", """E305""", 556.2302166348635],
    
    ["""4-(p-Tolyl)butanoic acid""", """E306""", 556.0727711384167],
    
    ["""1-Boc-4-Methylpiperidine-4-carboxylic acid""", """E307""", 406.0152075626798],
    
    ["""1-Methyl-1-cyclohexanecarboxylic acid""", """E308""", 1745.587201125176],
    
    ["""1-Cbz-4-methylpiperidine-4-carboxylic acid""", """E309""", 490.7380224297718],
    
    ["""Indomethacin""", """E310""", 505.0537730575739],
    
    ["""ciprofibrate""", """E311""", 545.3460141794916],
    
    ["""Fenbufen""", """E312""", 729.9424571338682],
    
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
        



