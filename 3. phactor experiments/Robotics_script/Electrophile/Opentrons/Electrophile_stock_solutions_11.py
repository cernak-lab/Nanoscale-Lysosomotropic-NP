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
    
    ["""p-Tolylacetic acid""", """E265""", 528.7295731504295],
    
    ["""2-(Trifluoromethyl)benzoic acid""", """E266""", 520.9835893120134],
    
    ["""5-thiophen-2-yl-1H-pyrazole-3-carboxylic acid""", """E267""", 509.90654446218014],
    
    ["""Tetrahydrofuran-3-carboxylic acid""", """E268""", 685.0018086297475],
    
    ["""o-Tolylacetic acid""", """E269""", 528.7295731504295],
    
    ["""Tolfenamic acid""", """E270""", 414.8286205578907],
    
    ["""Tetrahydro-2H-pyran-2-carboxylic acid""", """E271""", 610.7226064238513],
    
    ["""m-Tolylacetic acid""", """E272""", 528.7295731504295],
    
    ["""3-(Trifluoromethoxy)benzoic acid""", """E273""", 480.1542790607413],
    
    ["""trans-Indole-3-acrylic acid""", """E274""", 529.2165713980448],
    
    ["""3-(Trifluoromethyl)benzoic acid""", """E275""", 520.9835893120134],
    
    ["""2-Tetrahydrofuroic Acid""", """E276""", 685.0018086297475],
    
    ["""2-(6-(Trifluoromethyl)pyridin-3-yl)acetic Acid""", """E277""", 482.4957344123238],
    
    ["""1H-TETRAZOLYL-1-ACETIC ACID, 98%""", """E278""", 620.5608556483721],
    
    ["""10-Undecenoic Acid""", """E279""", 537.6819341184131],
    
    ["""Tetrahydropyran-4-carboxylic acid""", """E280""", 610.727330008683],
    
    ["""P-TOLUIC ACID, 98%""", """E281""", 817.0221079691515],
    
    ["""Vanillic acid""", """E282""", 589.7071067499256],
    
    ["""2-Bromopropionic Acid""", """E283""", 518.9783617702818],
    
    ["""2-Hydroxy-2-(4-methylphenyl)acetic acid""", """E284""", 477.4346753324908],
    
    ["""4-(Dimethylcarbamoyl)benzoic acid""", """E285""", 512.5983436853003],
    
    ["""1-Cyclopentene-1-carboxylic acid""", """E286""", 709.4575938642647],
    
    ["""(E)-3,4-Dimethoxycinnamic acid""", """E287""", 475.28432832236683],
    
    ["""(E)-4-Oxo-4-phenylbut-2-enoic acid""", """E288""", 562.6335357892945],
    
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
        



