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
    
    ["""3,5-DI-TERT-BUTYL-4-HYDROXYBENZOIC ACID, 97%""", """E121""", 473.36723524947064],
    
    ["""2-acetyloxybenzoic acid""", """E122""", 550.0621669626998],
    
    ["""3-methoxybenzoic acid""", """E123""", 652.2461386789353],
    
    ["""9,10-dioxoanthracene-2-carboxylic acid""", """E124""", 414.96801998255484],
    
    ["""2-acetamidoprop-2-enoic acid""", """E125""", 769.5333436604443],
    
    ["""2-acetylbenzoic acid""", """E126""", 604.1617933723197],
    
    ["""4-acetamidobenzoic acid""", """E127""", 553.1291510855613],
    
    ["""azetidine-3-carboxylic acid""", """E128""", 787.2957467853611],
    
    ["""4-acetylbenzoic acid""", """E129""", 604.1617933723197],
    
    ["""azetidine-2-carboxylic acid""", """E130""", 866.0253214638972],
    
    ["""adamantane-1-carboxylic acid""", """E131""", 549.8158011540169],
    
    ["""3-(4-bromophenyl)propanoic acid""", """E132""", 431.54778015453786],
    
    ["""1-benzylpiperidine-4-carboxylic acid""", """E133""", 451.0379423568041],
    
    ["""1,3-benzothiazole-6-carboxylic acid""", """E134""", 553.0357142857143],
    
    ["""4-bromo-3,5-dihydroxybenzoic acid""", """E135""", 424.1477126426916],
    
    ["""2-bromo-1,3-thiazole-4-carboxylic acid""", """E136""", 589.8392232263026],
    
    ["""5-bromofuran-2-carboxylic acid""", """E137""", 518.6150382238977],
    
    ["""but-2-ynoic acid""", """E138""", 947.5879624122755],
    
    ["""(1S,2R)-2-benzamidocyclohexane-1-carboxylic acid""", """E139""", 415.35885802094714],
    
    ["""benzoic acid""", """E140""", 830.1440222731738],
    
    ["""cyclopentanecarboxylic acid""", """E141""", 696.8936393902225],
    
    ["""4-cyclohexylbenzoic acid""", """E142""", 484.57211397238814],
    
    ["""3-cyclohexylpropanoic acid""", """E143""", 508.0983228779926],
    
    ["""2-(4-chlorophenyl)acetic acid""", """E144""", 581.2008324051819],
    
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
        



