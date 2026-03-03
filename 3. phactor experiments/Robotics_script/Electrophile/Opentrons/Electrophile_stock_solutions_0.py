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
    
    ["""2-BIBENZYLCARBOXYLIC ACID, 97%""", """E1""", 436.949882883281],
    
    ["""2-CHLORO-5-(TRIFLUOROMETHYL)ISONICOTINIC ACID, 97%""", """E2""", 438.36067390822427],
    
    ["""4-HYDROXYBENZOIC ACID, 99%""", """E3""", 719.0081088908196],
    
    ["""4-METHOXYBENZOIC ACID, 97%""", """E4""", 652.2461386789353],
    
    ["""3-(4-METHOXYPHENYL)PROPIONIC ACID, 98%""", """E5""", 549.9389567147614],
    
    ["""3-(METHOXYCARBONYL)BENZOIC ACID, 98%""", """E6""", 550.0621669626998],
    
    ["""1-METHYLINDOLE-3-CARBOXYLIC ACID, 97%""", """E7""", 565.8414202534535],
    
    ["""4-FLUOROBENZOIC ACID, 98%""", """E8""", 566.9799443294553],
    
    ["""4-PHENOXYBENZOIC ACID, 97%""", """E9""", 461.8098216786482],
    
    ["""5-METHYL-2-NITROBENZOIC ACID, 98%""", """E10""", 547.0287054926856],
    
    ["""4-(DIMETHYLAMINO)PHENYLACETIC ACID, 97%""", """E11""", 552.9734404642339],
    
    ["""ISOVALERIC ACID, 99%""", """E12""", 584.4865367668658],
    
    ["""2-(BROMOMETHYL)BENZOIC ACID, 97%""", """E13""", 460.0297619047619],
    
    ["""4-CARBOXYBENZALDEHYDE, 97%""", """E14""", 661.0893891960301],
    
    ["""4-METHYLVALERIC ACID, 99%""", """E15""", 855.8815426997246],
    
    ["""3-(DIMETHYLAMINO)BENZOIC ACID, 97%""", """E16""", 600.3635207942368],
    
    ["""4-CYANO-3-NITROBENZOIC ACID, 98%""", """E17""", 515.4809243741217],
    
    ["""2-HYDROXYISOBUTYRIC ACID, 99%""", """E18""", 764.4918347742555],
    
    ["""DL-PIPECOLINIC ACID, 98%""", """E19""", 769.233508826262],
    
    ["""PARA-METHOXYCINNAMIC ACID, 99%, PREDOMINANTLY TRANS""", """E20""", 556.2302166348635],
    
    ["""2-PHENYLPROPIONIC ACID, 97%""", """E21""", 660.911966438037],
    
    ["""3-CYCLOPENTENE-1-CARBOXYLIC ACID, 98%""", """E22""", 886.8219923303309],
    
    ["""5-HEXENOIC ACID, 98%""", """E23""", 871.1170492377781],
    
    ["""4-nitro-3-(trifluoromethyl)benzoic acid""", """E24""", 420.3147329023477],
    
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


