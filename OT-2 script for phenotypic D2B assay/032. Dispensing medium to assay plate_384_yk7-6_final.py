#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
from opentrons import protocol_api
from pandas import DataFrame

metadata = {
    'apiLevel': '2.13',
    'protocolName': 'Dispense Medium to assay plate',
    'description': '''This protocol dispenses 100 µL of medium into each well of a 384-well assay plate.''',
    'author': 'ykao'
}

def run(protocol: protocol_api.ProtocolContext):
    tips = protocol.load_labware('geb_96_tiprack_1000ul', 1)
    reservoir = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', 2)
    assay_plate = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', 5)
    locations = assay_plate.wells()[:]
    p1000 = protocol.load_instrument('p1000_single', 'left', tip_racks=[tips])

    p1000.well_bottom_clearance.aspirate = 7
    p1000.well_bottom_clearance.dispense = 7

    p1000.flow_rate.aspirate = 400
    p1000.flow_rate.dispense = 300
    p1000.flow_rate.blow_out = 500
    p1000.default_speed = 400
    p1000.pick_up_tip()

    group_size = 8
    # Dispense to the first 192 wells from A3
    # require 22 mL medium per tube
    for i in range(0, 192,group_size):  
        p1000.aspirate(900, reservoir['A3'])
        # p1000.air_gap(5)  # Add a 5 µL air gap after aspirating 300 µL
        for loc in locations[i:i+group_size]: 
            p1000.flow_rate.dispense = 250  # Specify dispensing speed for medium
            p1000.dispense(100, loc)
        p1000.blow_out(reservoir['A3'])  # Blow out remaining medium back into tube_rack['A3']

    # Switch to reservoir A4 for wells 193-384
    # require 22 mL medium per tube
    for i in range(192, len(locations), group_size):
        p1000.aspirate(900, reservoir['A4'])
    #    p1000.air_gap(5)  # Add a 5 µL air gap after aspirating 300 µL
        for loc in locations[i:i+group_size]:
            p1000.flow_rate.dispense = 250  # Specify dispensing speed for medium
            p1000.dispense(100, loc)
        p1000.blow_out(reservoir['A4'])  # Blow out remaining medium back into tube_rack['A4']

    p1000.drop_tip()

    # Reset to the original flow rates if needed for other steps
    
