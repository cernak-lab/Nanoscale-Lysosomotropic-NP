#!/usr/bin/env python
# coding: utf-8

# In[60]:


import pandas as pd
import numpy as np
from opentrons import protocol_api
from pandas import DataFrame


# In[59]:


metadata = {
    'apiLevel': '2.13',
    'protocolName': '''yu-ting-experiment-Nucleophile_sourceplates''',
    'description': '''yu-ting-experiment-Nucleophile_sourceplates''',
    'author': """ykao"""
    }


# In[83]:


# volumes = pd.read_csv("opentrons_protocol_data.csv")

# volumes['volumePerSourcePlateWell_uL'] = volumes['volumePerSourcePlateWell_uL'].fillna(100).astype("float").astype("int")
# volumes = volumes[['nanochem name','volumePerSourcePlateWell_uL']].set_index("nanochem name")['volumePerSourcePlateWell_uL'].to_dict()
# volumes


# In[ ]:


volumes = {

    'L1' : 52.72395171537484,
    
    'C1' : 41.3908389100293,
    
    'N1' : 25,
    
    'N2' : 25,
    
    'N3' : 25,
    
    'N4' : 25,
    
    'O1' : 43.81545308938583,

    'W' : 50,
    
    
}

# In[99]:


rows = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']
columns = [str(i+1) for i in range(24)] #note: not using all 24 columns

locations = [f"{r}{c}" for c in columns for r in rows]


# In[89]:

srcPlateMap = """L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1	W
L1	C1	N1	N2	N3	N4	O1 W"""



srcPlateMap = [row.split() for row in srcPlateMap.split("\n")]

srcPlateLocs = np.array(srcPlateMap).T.flatten()

location_substs = dict(zip(locations,srcPlateLocs))
location_substs_rev = {}
for k,v in location_substs.items():
    location_substs_rev[v] = location_substs_rev.get(v,[]) + [k]


# In[86]:


def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware('opentrons_96_tiprack_300ul', 5) 
    vials = protocol.load_labware('analytical_24_tuberack_3696.9ul', 1) # previous one analyticalsales_24_tuberack_7400ul
    location = vials.wells()
    reservoir = protocol.load_labware('opentrons_6_tuberack_falcon_50ml_conical', 3)
    plate_384 = protocol.load_labware('analyticalsales_384_wellplate_120ul', 2)
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tips]) 
    p300.well_bottom_clearance.aspirate = 2
    p300.well_bottom_clearance.dispense = 5
    #p300.flow_rate.aspirate = 50

     #WASH COLUMNS
    #wash_volume = 100 #ul per well
    #p300.pick_up_tip()
    #for loc in location_substs_rev['W']:
         #p300.transfer(wash_volume, reservoir['A3'], plate_384[loc], new_tip = 'never')
    #p300.drop_tip()
     #SUBSTANCE COLUMNS
    
    
    substs_ = list(enumerate(list(volumes.items())[0:24])) #24 at a time
    for i,(subst,vol) in substs_: 
        p300.pick_up_tip()
        for loc in location_substs_rev[subst]:
            p300.transfer(vol, location[i], plate_384[loc], mix_before = (2, 100), new_tip = 'never')
        p300.drop_tip()
        
