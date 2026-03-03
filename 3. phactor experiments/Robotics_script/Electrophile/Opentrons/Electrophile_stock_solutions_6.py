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
    
    ["""2-(2-chlorophenyl)acetic acid""", """E145""", 581.2008324051819],
    
    ["""2-(4-chlorophenyl)propanoic acid""", """E146""", 536.6531253385332],
    
    ["""2-(2-cyanophenyl)acetic acid""", """E147""", 615.5013651030031],
    
    ["""1-phenylmethoxycarbonylpiperidine-4-carboxylic acid""", """E148""", 464.76357628470504],
    
    ["""5-(4-chlorophenyl)furan-2-carboxylic acid""", """E149""", 444.19593926870897],
    
    ["""2-(3-chlorophenyl)acetic acid""", """E150""", 685.8169822381149],
    
    ["""3-cyanobenzoic acid""", """E151""", 539.7368313736151],
    
    ["""3-cyclopentylpropanoic acid""", """E152""", 558.5879043600562],
    
    ["""2-phenylquinoline-4-carboxylic acid""", """E153""", 412.0350156463131],
    
    ["""3,4-difluorobenzoic acid""", """E154""", 502.0088551549652],
    
    ["""3-(4,5-diphenyl-1,3-oxazol-2-yl)propanoic acid""", """E155""", 436.7321854756222],
    
    ["""2,3-dihydro-1H-indene-2-carboxylic acid""", """E156""", 611.5988407941793],
    
    ["""2,2-diphenylacetic acid""", """E157""", 559.3976630229928],
    
    ["""2,6-dimethylpyridine-3-carboxylic acid""", """E158""", 656.5506747816883],
    
    ["""3,5-difluorobenzoic acid""", """E159""", 627.5110689437065],
    
    ["""2,6-difluorobenzoic acid""", """E160""", 627.5110689437065],
    
    ["""2-(2,6-dimethoxyanilino)-2-oxoacetic acid""", """E161""", 439.04973357015984],
    
    ["""3,5-dichloropyridine-2-carboxylic acid""", """E162""", 515.8333333333334],
    
    ["""2-(11-oxo-6H-benzo[c][1]benzoxepin-2-yl)acetic acid""", """E163""", 441.32721986132856],
    
    ["""2-(3,4-dimethoxyphenyl)acetic acid""", """E164""", 504.683995922528],
    
    ["""2,3-difluorobenzoic acid""", """E165""", 627.5110689437065],
    
    ["""2,4-difluorobenzoic acid""", """E166""", 627.5110689437065],
    
    ["""1,5-dimethylpyrazole-3-carboxylic acid""", """E167""", 566.8577137148566],
    
    ["""2-(3,5-difluorophenyl)acetic acid""", """E168""", 564.4371289141927],
    
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
        

