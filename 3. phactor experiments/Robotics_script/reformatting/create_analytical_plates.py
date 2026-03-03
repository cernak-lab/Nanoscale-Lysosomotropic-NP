#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import numpy as np
from opentrons import protocol_api
from pandas import DataFrame


# In[2]:


metadata = {
    'apiLevel': '2.13',
    'protocolName': 'createAnalyticalPlates_yk',
    'description': '''This analytical plate will be dispensed pure DMSO for bioassay and lc-ms analysis''',
    'author': 'ykao'
    }


# In[ ]:


def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware('opentrons_96_tiprack_300ul', 5) #load_labware(self, load_name: 'str', location: 'DeckLocation', label: 'Optional[str]' = None, namespace: 'Optional[str]' = None, version: 'Optional[int]' = None) → 'Labware'¶

    reservoir = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', 3)

    # vials = protocol.load_labware('custom462dramstirrer_24_tuberack_7400ul', 10)
#     vials = protocol.load_labware('corning_24_wellplate_3.4ml_flat', 7) #just for testing
#     location = vials.wells()

#     plate_384 = protocol.load_labware('analyticalsales_384_wellplate_120ul', 1)

    analyticalPlate_384 = protocol.load_labware('fisher_384_wellplate_58ul', 2)
    locations = analyticalPlate_384.wells()

    p300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tips]) #load_instrument(self, instrument_name: 'str', mount: 'Union[Mount, str]', tip_racks: 'Optional[List[Labware]]' = None, replace: 'bool' = False) → 'InstrumentContext'

    p300.well_bottom_clearance.aspirate = 9
    p300.well_bottom_clearance.dispense = 4
    #p300.flow_rate.aspirate = 50

    p300.pick_up_tip()
    p300.distribute(30, reservoir['A3'], locations, new_tip = 'never', blow_out=True, blowout_location="source well")
    p300.drop_tip()
