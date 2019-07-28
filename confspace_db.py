
#order for fields: cap ID,isExtended , offset , bit_loc , size
#if cap id not relevant (for example you want read from header) put 1 in the cap id&isExtended
class ConfigurationSpaceDb:
    REGISTERS = {
        'link disable': [0X10, False, 0X10, 4, 1],
        'current link speed': [0x10, False, 0x12, 0, 4],
        'target link speed': [0x10, False, 0x30, 0, 4],
        'retrain_link': [0x10, False, 0x10, 5, 1],
        'negotiated link width': [0x10, False, 0x12, 4, 6],
        'header type': [-1, -1, 0x0E, 0, 7],
        'Secondary Bus Reset': [-1, -1, 0x3E, 6, 1],
        'vendor_id': [-1, -1, 0x00, 0, 16],


    }

# #order for fields: offset, bit_loc, size
# class ConfigurationSpaceHeader:
#     REGISTERS = {
#         'header type': [0x0E, 0, 7],
#         'Secondary Bus Reset': [0x3E, 6, 1],
#         'vendor_id': [0x00, 0, 16],
#
#     }

