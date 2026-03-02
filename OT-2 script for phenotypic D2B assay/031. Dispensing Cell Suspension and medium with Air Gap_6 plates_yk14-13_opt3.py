import pandas as pd
import numpy as np
from opentrons import protocol_api
from pandas import DataFrame

metadata = {
    'protocolName': 'Dispense Cell Suspension and medium using p10_multi for 3 plates and mix every 12 cols with dif clearance',
    'author': 'ykao <ykao@umich.edu>',
    'description': 'Protocol to dispense cell suspension into 384 well plate',
    'apiLevel': '2.12',  # opentrons version 7.10
}

def run(protocol: protocol_api.ProtocolContext):
    # labware
     # Tip rack loading
    tiprack_10_1 = protocol.load_labware('geb_96_tiprack_10ul', location=10)
    # tiprack_300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', location=5)
    # reservoir and assay plate
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 8) 
    assay_plate1 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', location=4)
    assay_plate2 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', location=5)
    assay_plate3 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', location=6)
    #assay_plate4 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', location=10) 
    #assay_plate5 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', location=4)
    #assay_plate6 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', location=2)

    assay_plate_list = [assay_plate1, assay_plate2, assay_plate3]
    # # liquids
    assay_son_a = reservoir['A1'] 
    #assay_son_a = reservoir['A4'] #for testing so chang to the second well
    assay_son_b = reservoir['A2']
    #assay_son_b = reservoir['A1']
    assay_son_c = reservoir['A3']
    #assay_son_d = reservoir['A7']
    #assay_son_e = reservoir['A8']
    #assay_son_f = reservoir['A9']
    medium = reservoir['A4']

    assay_son_1_list = [assay_son_a, assay_son_b, assay_son_c]
    # pipette
    p10_multi = protocol.load_instrument('p10_multi', 'right', tip_racks=[tiprack_10_1])

    # set flow rates and speed
    p10_multi.flow_rate.aspirate = 500
    p10_multi.flow_rate.dispense = 400
    p10_multi.flow_rate.blow_out = 500
    p10_multi.default_speed = 400
    
    #p10_multi.well_bottom_clearance.aspirate = 5
    #p10_multi.well_bottom_clearance.dispense = 5
       
    for j in range(3):
        assay_son_1 = assay_son_1_list[j]
        assay_plate = assay_plate_list[j]
        
        p10_multi.pick_up_tip()
        for row_place in ['A', 'B']:
            # Define the well locations for the source and destination plates
            assay_wells = assay_plate.rows_by_name()[row_place][:192]  # First row for multichannel
            # Iterate over each group of wells (8 columns at a time since using a multichannel pipette)
            if row_place == 'A' :
                for i in range(23):  # 48 wells, 8 at a time = 6 iterations
                    if i == 0:
                        for _ in range(8):
                                p10_multi.aspirate(10, assay_son_1.bottom(2))
                                p10_multi.dispense(10, assay_son_1.bottom(15))
                    if i == 11:
                        for _ in range(8):
                                p10_multi.aspirate(10, assay_son_1.bottom(2))
                                p10_multi.dispense(10, assay_son_1.bottom(10)) 
                    for _ in range(2):
                        p10_multi.aspirate(10, assay_son_1.bottom(2))  # Aspirate from source well
                        p10_multi.dispense(10, assay_wells[i].bottom())  # Dispense into assay well
                        p10_multi.blow_out(assay_wells[i].bottom())  # Blow out at the destination wells

            if row_place == 'B':
                for i in range(23):  # 48 wells, 8 at a time = 6 iterations
                    if i == 0:
                        for _ in range(8):
                                p10_multi.aspirate(10, assay_son_1.bottom(2))
                                p10_multi.dispense(10, assay_son_1.bottom(8))
                    if i == 11:
                        for _ in range(8):
                                p10_multi.aspirate(10, assay_son_1.bottom(2))
                                p10_multi.dispense(10, assay_son_1.bottom(5)) 
                    for _ in range(2):
                        p10_multi.aspirate(10, assay_son_1.bottom(2))  # Aspirate from source well
                        p10_multi.dispense(10, assay_wells[i].bottom())  # Dispense into assay well
                        p10_multi.blow_out(assay_wells[i].bottom())  # Blow out at the destination wells        
        p10_multi.drop_tip()
        p10_multi.pick_up_tip()
        for row_place in ['A', 'B']:
            # Define the well locations for the source and destination plates
            assay_wells = assay_plate.rows_by_name()[row_place][:192]  # First row for multichannel
            # Iterate over each group of wells (8 columns at a time since using a multichannel pipette)
            for _ in range(1):
                        p10_multi.aspirate(10, medium.bottom(2))
                        p10_multi.dispense(10, medium.bottom(8))
            for i in range(24):  # 48 wells, 8 at a time = 6 iterations
                if i == 23:
                    for _ in range(2):
                        p10_multi.aspirate(10, medium.bottom(2))  # Aspirate from source well
                        p10_multi.dispense(10, assay_wells[i].bottom())  # Dispense into assay well
                        p10_multi.blow_out(assay_wells[i].bottom())  # Blow out at the destination well
                           
        p10_multi.drop_tip()