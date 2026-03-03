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
    
    ["""6-methoxypyridine-3-carboxylic acid""", """E217""", 647.997257411519],
    
    ["""6-methylpyridine-3-carboxylic acid""", """E218""", 434.50911477322444],
    
    ["""5-methyl-2-phenyltriazole-4-carboxylic acid""", """E219""", 643.0062992125984],
    
    ["""2-(6-methylpyridin-3-yl)acetic acid""", """E220""", 525.2405398253505],
    
    ["""2-(1,3-benzodioxol-5-yl)acetic acid""", """E221""", 550.0621669626998],
    
    ["""2-(6-methoxypyridin-3-yl)acetic acid""", """E222""", 593.2292414453218],
    
    ["""(2S)-2-(6-methoxynaphthalen-2-yl)propanoic acid""", """E223""", 429.2916702857639],
    
    ["""1-methylpyrrole-2-carboxylic acid""", """E224""", 476.5013186286262],
    
    ["""4-methyl-1,3-thiazole-5-carboxylic acid""", """E225""", 554.7762799469162],
    
    ["""2-(2-methoxyphenyl)acetic acid""", """E226""", 596.7933441656135],
    
    ["""3-methylbut-2-enoic acid""", """E227""", 596.2808629644426],
    
    ["""1-methylpiperidine-4-carboxylic acid""", """E228""", 554.7372538063975],
    
    ["""2-(3-methyl-1,2-oxazol-5-yl)acetic acid""", """E229""", 703.6167800453514],
    
    ["""6-methoxynaphthalene-2-carboxylic acid""", """E230""", 489.53538400672556],
    
    ["""2-(1-methylpyrazol-4-yl)acetic acid""", """E231""", 566.8577137148566],
    
    ["""2-methoxypyridine-4-carboxylic acid""", """E232""", 518.3978059292151],
    
    ["""3-(3-methylphenyl)propanoic acid""", """E233""", 483.21071863581],
    
    ["""naphthalene-2-carboxylic acid""", """E234""", 460.6300383319781],
    
    ["""1-methyl-5-phenylpyrazole-3-carboxylic acid""", """E235""", 489.53538400672556],
    
    ["""4-nitrobenzoic acid""", """E236""", 474.6979415988511],
    
    ["""2-nitrobenzoic acid""", """E237""", 474.6979415988511],
    
    ["""2-(2-nitrophenyl)acetic acid""", """E238""", 656.4344465912226],
    
    ["""naphthalene-1-carboxylic acid""", """E239""", 575.7875479149727],
    
    ["""pyridine-3-carboxylic acid""", """E240""", 484.36901957598894],
    
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
        



