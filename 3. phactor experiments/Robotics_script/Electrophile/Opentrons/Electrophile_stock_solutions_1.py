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
    
    ["""2-BROMOBENZOIC ACID, 97%""", """E25""", 492.4629390110436],
    
    ["""16-HYDROXYHEXADECANOIC ACID, 98%""", """E26""", 434.4962924895381],
    
    ["""4'-HYDROXYAZOBENZENE-2-CARBOXYLIC ACID""", """E27""", 407.83078066300624],
    
    ["""4-IODOBENZOIC ACID, 98%""", """E28""", 438.012619950004],
    
    ["""(1R)-(-)-10-CAMPHORSULFONIC ACID, 98%""", """E29""", 425.4778303917348],
    
    ["""4-Bromophenylacetic acid""", """E30""", 460.0297619047619],
    
    ["""LEVULINIC ACID, 98+%""", """E31""", 1267.2533459650333],
    
    ["""(2R)-3-HYDROXY-2-(PHENYLMETHOXYCARBONYLAMINO)PROPANOIC ACID - [H68524]""", """E32""", 413.025248725023],
    
    ["""2-(2,3-DIHYDRO-1H-INDEN-2-YL)ACETIC ACID, 98%""", """E33""", 562.5046819136256],
    
    ["""1H-IMIDAZOLE-4-CARBOXYLIC ACID, 95%""", """E34""", 887.1402444464269],
    
    ["""3-IODOBENZOIC ACID, 98%""", """E35""", 414.1210224981856],
    
    ["""MERCAPTOACETIC ACID 98%""", """E36""", 864.4324793747286],
    
    ["""3-METHOXY-4-METHYLBENZOIC ACID, 98%""", """E37""", 596.7933441656135],
    
    ["""3-(METHOXYCARBONYL)CYCLOHEXANECARBOXYLIC ACID, 95+%""", """E38""", 532.0569280343717],
    
    ["""3-(2-METHOXYPHENYL)PROPIONIC ACID, 98%""", """E39""", 549.9389567147614],
    
    ["""6-METHOXYINDOLE-2-CARBOXYLIC ACID, 95%""", """E40""", 518.0672664504655],
    
    ["""2-METHOXY-4-METHYLBENZOIC ACID, 97%""", """E41""", 596.7933441656135],
    
    ["""(±)-ALPHA-METHYLHYDROCINNAMIC ACID, 98%""", """E42""", 604.0133982947624],
    
    ["""3-(TERT-BUTYL)-1-METHYL-1H-PYRAZOLE-CARBOXYLIC ACID, 95%""", """E43""", 543.7871803314674],
    
    ["""4-PYRAZOLECARBOXYLIC ACID, 97+%""", """E44""", 709.7121955571415],
    
    ["""4-PHENYLBUTYRIC ACID 99%""", """E45""", 604.0133982947624],
    
    ["""5-PHENYLVALERIC ACID, 99.0+%""", """E46""", 556.0727711384167],
    
    ["""1-TRIFLUOROMETHYLCYCLOPROPANE-1-CARBOXYLIC ACID, 98%""", """E47""", 643.9713803621258],
    
    ["""(S)-1-(TERT-BUTOXYCARBONYL)PIPERIDINE-3-CARBOXYLIC ACID, 97%""", """E48""", 431.16696471409256],
    
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
        

