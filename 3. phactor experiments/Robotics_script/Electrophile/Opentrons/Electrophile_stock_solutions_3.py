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
    
    ["""4-(FMOC-AMINOMETHYL)BENZOIC ACID, 95%""", """E73""", 420.4949116229245],
    
    ["""3-(5-(2-FLUOROPHENYL)-1,2,4-OXADIAZOL-3-YL)BENZOIC ACID, 98%""", """E74""", 416.1784407542921],
    
    ["""4-FLUORO-1-NAPHTHOIC ACID, 97%""", """E75""", 520.8452963138245],
    
    ["""2-(FLUOROSULFONYL)DIFLUOROACETIC ACID""", """E76""", 556.5138413161884],
    
    ["""2-FLUORO-4-NITROBENZOIC ACID, 98%""", """E77""", 535.2193290475933],
    
    ["""1-(4-FLUOROPHENYL)CYCLOPROPANECARBOXYLIC ACID, 97+%""", """E78""", 550.0313592717989],
    
    ["""8-FLUOROQUINOLINE-2-CARBOXYLIC ACID""", """E79""", 518.1219920485457],
    
    ["""2-FLUORO-6-(TRIFLUOROMETHYL)BENZOIC ACID, 98%""", """E80""", 618.1696458603623],
    
    ["""2-METHOXY-2-(NAPHTHALEN-1-YL)PROPANOIC ACID, 97%""", """E81""", 429.2916702857639],
    
    ["""2-METHYL-4-NITROBENZOIC ACID, 98%""", """E82""", 547.0287054926856],
    
    ["""4-(METHOXYCARBONYL)CYCLOHEXANECARBOXYLIC ACID""", """E83""", 808.7265306122449],
    
    ["""6-METHYLPYRIDINE-2-CARBOXYLIC ACID, 98.0+%""", """E84""", 579.3454863642993],
    
    ["""3-METHYL-4-PENTENOIC ACID, 97%""", """E85""", 696.8936393902225],
    
    ["""4-MERCAPTOBENZOIC ACID, 90%""", """E86""", 643.5504896556197],
    
    ["""2-MERCAPTOPROPIONIC ACID, 95%""", """E87""", 749.6504945831371],
    
    ["""MEFENAMIC ACID""", """E88""", 491.34748010610076],
    
    ["""ANTI-3-OXOTRICYCLO[2.2.1.02,6]HEPTANE-7-CARBOXYLIC ACID""", """E89""", 652.2461386789353],
    
    ["""3-BENZOYLPROPIONIC ACID, 98%""", """E90""", 556.2302166348635],
    
    ["""(BENZHYDRYLTHIO)ACETIC ACID, 98.0+%""", """E91""", 420.3614014711575],
    
    ["""1-benzylpiperidine-3-carboxylic acid""", """E92""", 451.0379423568041],
    
    ["""4-BIPHENYLCARBOXYLIC ACID, 99%""", """E93""", 499.48996064978303],
    
    ["""2-BROMOISONICOTINIC ACID, 98%""", """E94""", 490.0249987624375],
    
    ["""5-BROMO-2-IODOBENZOIC ACID, 98.0+%""", """E95""", 421.2524242146156],
    
    ["""4-BUTYLBENZOIC ACID, 97%""", """E96""", 556.0727711384167],
    
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
        



