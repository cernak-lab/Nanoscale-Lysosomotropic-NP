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
    
    ["""2-[2,3-dichloro-4-(2-methylidenebutanoyl)phenoxy]acetic acid""", """E169""", 428.8567347342724],
    
    ["""2-(2-ethylsulfonylphenyl)acetic acid""", """E170""", 433.0777149866386],
    
    ["""2-ethyl-5-methylpyrazole-3-carboxylic acid""", """E171""", 643.6346241162353],
    
    ["""2-(5-fluoropyridin-2-yl)acetic acid""", """E172""", 639.6206407529168],
    
    ["""2-fluoro-2-phenylacetic acid""", """E173""", 643.7608667445179],
    
    ["""2-(4-fluorophenyl)acetic acid""", """E174""", 643.7608667445179],
    
    ["""2-fluorobenzoic acid""", """E175""", 566.9799443294553],
    
    ["""2-(2-fluorophenyl)acetic acid""", """E176""", 515.0086933956144],
    
    ["""3-(3-fluorophenyl)propanoic acid""", """E177""", 707.60608943863],
    
    ["""furan-3-carboxylic acid""", """E178""", 709.775874375446],
    
    ["""3-(4-fluorophenyl)propanoic acid""", """E179""", 471.7373929590866],
    
    ["""furan-2-carboxylic acid""", """E180""", 709.775874375446],
    
    ["""9H-fluorene-9-carboxylic acid""", """E181""", 470.6695048280455],
    
    ["""2-(furan-2-yl)acetic acid""", """E182""", 630.3668226151772],
    
    ["""3-fluorobenzoic acid""", """E183""", 566.9799443294553],
    
    ["""3-(2-fluorophenyl)propanoic acid""", """E184""", 471.7373929590866],
    
    ["""3-hydroxy-4-methylbenzoic acid""", """E185""", 521.7969109431482],
    
    ["""(2E,4E)-hexa-2,4-dienoic acid""", """E186""", 532.0931953981985],
    
    ["""2-benzamidoacetic acid""", """E187""", 442.50332086844895],
    
    ["""3-phenylpropanoic acid""", """E188""", 528.7295731504295],
    
    ["""2-(4-hydroxy-3-methoxyphenyl)acetic acid""", """E189""", 543.9378053466543],
    
    ["""2-(3-hydroxy-4-methoxyphenyl)acetic acid""", """E190""", 543.9378053466543],
    
    ["""2-(1H-indol-3-yl)acetic acid""", """E191""", 565.8414202534535],
    
    ["""piperidine-4-carboxylic acid""", """E192""", 461.5401052957572],
    
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
        



