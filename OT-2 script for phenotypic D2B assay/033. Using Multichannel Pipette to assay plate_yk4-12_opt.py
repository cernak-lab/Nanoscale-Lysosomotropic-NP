#!/usr/bin/env python
# coding: utf-8
#opentrons_simulate C:\Users\carlm\PycharmProjects\pythonProject\CernakLabPython\MTT_Antifungal_Assay_V1.py --custom-labware-path C:\Users\carlm\PycharmProjects\pythonProject\CernakLabPython
#opentrons_simulate C:/Users/gaoyuting/Desktop/1536 design/03. assay plate/033. Using Multichannel Pipette to assay plate.py --custom-labware-path C:/Users/gaoyuting/Desktop/1536 design/03. assay plate/labware

import pandas as pd
import numpy as np
from opentrons import protocol_api
from pandas import DataFrame
import math
metadata = {
    'apiLevel': '2.13',
    'protocolName': 'Assay Plate Dispensing with Multichannel Pipette',
    'description': '''This protocol transfers 3 µL of reaction crude in DMSO from a custom 384-well plate to an assay plate with pre-dispensed medium, with mixing. Then, it uses the same tip to dispense 10 µL into three assay running plates. The tip is dropped after completing all steps for each well using a multichannel pipette.''',
    'author': 'ykao'
}

def run(protocol: protocol_api.ProtocolContext):
    # Tip rack loading
    tiprack_10_1 = protocol.load_labware('geb_96_tiprack_10ul', location=7)
    tiprack_10_2 = protocol.load_labware('geb_96_tiprack_10ul', location=8)
    tiprack_10_3 = protocol.load_labware('geb_96_tiprack_10ul', location=10)
    tiprack_10_4 = protocol.load_labware('geb_96_tiprack_10ul', location=11)
    tiprack_10_list = [tiprack_10_1, tiprack_10_2, tiprack_10_3, tiprack_10_4]

    # Labware loading
    reaction_plate = protocol.load_labware('fisher_384_wellplate_58ul', 4)
    Assay_Plate_384 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', 5)
    Assay_Running_Plate_1 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', 3)
    Assay_Running_Plate_2 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', 6)
    Assay_Running_Plate_3 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', 9)

    Assay_Running_Plate_list = [Assay_Running_Plate_1, Assay_Running_Plate_2, Assay_Running_Plate_3]
    # Load the pipette instrument outside the loop
    p10_multi = protocol.load_instrument('p10_multi', 'right', tip_racks=tiprack_10_list)

    # Set clearance and flow rates
    #p10_multi.well_bottom_clearance.aspirate = 5
    #p10_multi.well_bottom_clearance.dispense = 5
    p10_multi.flow_rate.aspirate = 500
    p10_multi.flow_rate.dispense = 400
    p10_multi.flow_rate.blow_out = 500
    p10_multi.default_speed = 400

    for row_place in ['A', 'B']:
        # Define the well locations for the source and destination plates
        source_wells = reaction_plate.rows_by_name()[row_place][:192]  # First row for multichannel
        assay_wells = Assay_Plate_384.rows_by_name()[row_place][:192]  # Assay wells
        assay_son1_wells = Assay_Running_Plate_1.rows_by_name()[row_place][:192]
        assay_son2_wells = Assay_Running_Plate_2.rows_by_name()[row_place][:192]
        assay_son3_wells = Assay_Running_Plate_3.rows_by_name()[row_place][:192]


        # Iterate over each group of wells (8 columns at a time since using a multichannel pipette)
        for i in range(24):  # 48 wells, 8 at a time = 6 iterations
            p10_multi.pick_up_tip()

            # Transfer 3 µL from source wells to assay wells (aspirate and dispense)
            p10_multi.aspirate(3, source_wells[i].bottom())  # Aspirate from source well
            p10_multi.dispense(3, assay_wells[i].bottom(5))  # Dispense into assay well
            p10_multi.blow_out(assay_wells[i].bottom(5))  # Blow out at the destination well

            # Perform mixing in assay wells
            for _ in range(10):
                p10_multi.aspirate(10, assay_wells[i].bottom(2))
                p10_multi.dispense(10, assay_wells[i].bottom(3))

            # Transfer 10 µL from assay wells to the three running plates
            for running_wells in [assay_son1_wells, assay_son2_wells, assay_son3_wells]:
                p10_multi.aspirate(10, assay_wells[i].bottom(2))  # Aspirate from assay well
                p10_multi.dispense(10, running_wells[i].bottom(1.5))  # Dispense into running plate well
                p10_multi.blow_out(running_wells[i].bottom(1.5))  # Blow out at the destination well

            p10_multi.drop_tip()