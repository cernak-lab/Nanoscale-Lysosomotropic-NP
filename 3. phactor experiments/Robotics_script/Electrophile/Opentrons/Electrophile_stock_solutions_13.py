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
    
    ["""Biotin""", """E313""", 566.0424460726126],
    
    ["""Ibufenac""", """E314""", 515.1560468140442],
    
    ["""Deoxycholic Acid""", """E315""", 449.48191543555777],
    
    ["""Bezafibrate""", """E316""", 379.95411829740186],
    
    ["""Indole-3-butyric acid""", """E317""", 487.02912812438495],
    
    ["""6-Methyl-2-(4-methylphenyl)imidazol[1,2-a]pyridine-3-acetic acid""", """E318""", 492.42922374429224],
    
    ["""Menbutone""", """E319""", 458.63183734788146],
    
    ["""1-Methyl-3-oxocyclobutanecarboxylic acid""", """E320""", 620.3658784047451],
    
    ["""Blank1""", """E321""", 0.0],
    
    ["""Blank2""", """E322""", 0.0],
    
    ["""Blank3""", """E323""", 0.0],
    
    ["""Blank4""", """E324""", 0.0],
    
    ["""Blank5""", """E325""", 0.0],
    
    ["""Blank6""", """E326""", 0.0],
    
    ["""Blank7""", """E327""", 0.0],
    
    ["""Blank8""", """E328""", 0.0],
    
    ["""Blank9""", """E329""", 0.0],
    
    ["""Blank10""", """E330""", 0.0],
    
    ["""Blank11""", """E331""", 0.0],
    
    ["""Blank12""", """E332""", 0.0],
    
    ["""Blank13""", """E333""", 0.0],
    
    ["""Blank14""", """E334""", 0.0],
    
    ["""Blank15""", """E335""", 0.0],
    
    ["""Blank16""", """E336""", 0.0],
    
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
        



