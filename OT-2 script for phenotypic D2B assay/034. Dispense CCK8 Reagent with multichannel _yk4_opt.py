import pandas as pd
import numpy as np
from opentrons import protocol_api
from pandas import DataFrame

metadata = {
    'protocolName': 'Dispense CCK-8 to assay running plate',
    'author': 'ykao <ykao@umich.edu>',
    'description': 'Protocol to dispense CCK-8 into 384 well plate with p10_multichannel',
    'apiLevel': '2.12',  # opentrons version 7.10
}

def run(protocol: protocol_api.ProtocolContext):
    # labware
    tiprack_10_1 = protocol.load_labware('geb_96_tiprack_10ul', location=10)
    
    # reservoir and assay plate 
    reservoir = protocol.load_labware('usascientific_12_reservoir_22ml', 8) 
    assay_plate1 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', location=4)
    assay_plate2 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', location=5)
    assay_plate3 = protocol.load_labware('thermoscientific164688_384_wellplate_120ul', location=6)
    assay_plate_list = [assay_plate1, assay_plate2, assay_plate3]
    # liquids
    cck = reservoir['A1']
    
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
            cck = reservoir['A1']
            assay_plate = assay_plate_list[j]
            p10_multi.pick_up_tip()
            for _ in range(3):
                        p10_multi.aspirate(10, cck.bottom(2))
                        p10_multi.dispense(10, cck.bottom(5))
            for row_place in ['A', 'B']:
                # Define the well locations for the source and destination plates
                assay_wells = assay_plate.rows_by_name()[row_place][:192]  # First row for multichannel
                # Iterate over each group of wells (8 columns at a time since using a multichannel pipette)
                for i in range(24):  # 48 wells, 8 at a time = 6 iterations        
                     p10_multi.aspirate(6, cck.bottom(2))  # Aspirate from source well
                     p10_multi.dispense(6, assay_wells[i].bottom(1))  # Dispense into assay well
                     p10_multi.blow_out(assay_wells[i].bottom(1))  # Blow out at the destination wells
                     #p10_multi.touch_tip(assay_wells[i], radius = 0.5, v_offset = -3, speed = 1)  # touchtip into assay well
            p10_multi.drop_tip()




    
