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
    
    ["""2,4-dioxo-1H-pyrimidine-6-carboxylic acid""", """E241""", 508.49199231262014],
    
    ["""(Z)-octadec-9-enoic acid""", """E242""", 558.3716814159292],
    
    ["""2-methylbenzoic acid""", """E243""", 831.6117884686007],
    
    ["""Pyridazine-4-carboxylic acid""", """E244""", 800.8017727639001],
    
    ["""3-(Pyridin-4-yl)propanoic acid""", """E245""", 525.2405398253505],
    
    ["""Pyrazinecarboxylic acid""", """E246""", 608.6093473005641],
    
    ["""1-PYRENEBUTYRIC ACID, 97%""", """E247""", 444.41918140825527],
    
    ["""3-(3-Pyridyl)propionic acid""", """E248""", 656.5506747816883],
    
    ["""2-(1H-Pyrazol-1-yl)benzoic acid""", """E249""", 421.1248804336273],
    
    ["""Pyrrole-2-carboxylic acid""", """E250""", 662.3666066606661],
    
    ["""PHENYLPROPIOLIC ACID 97%""", """E251""", 638.5188312576981],
    
    ["""Pyrimidine-2-carboxylic acid""", """E252""", 640.6414182111201],
    
    ["""1H-Pyrazole-3-carboxylic acid""", """E253""", 709.7121955571415],
    
    ["""2-Picolinic acid""", """E254""", 839.5729672650474],
    
    ["""TRIMETHYLACETIC ACID, 99%""", """E255""", 584.4865367668658],
    
    ["""1-Phenyl-1-cyclopropanecarboxylic acid""", """E256""", 489.2790726353434],
    
    ["""Phenylacetic acid""", """E257""", 583.5872199779654],
    
    ["""Quinoline-8-carboxylic acid""", """E258""", 457.9737829878154],
    
    ["""QUINALDIC ACID, 98.0+%""", """E259""", 572.4672287347693],
    
    ["""Retinoic acid""", """E260""", 426.25632490013317],
    
    ["""2-(4-Sulfamoylphenyl)acetic acid""", """E261""", 459.6192445291084],
    
    ["""4-SULFAMOYLBENZOIC ACID, 97%""", """E262""", 580.5811133200796],
    
    ["""2-Thiophenecarboxylic acid""", """E263""", 620.2684354272336],
    
    ["""4-(Trifluoromethoxy)benzoic Acid""", """E264""", 480.1542790607413],
    
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
        

