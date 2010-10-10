import logging

ALL = 0
DEBUG = 0+ALL
INFO = 0+ALL
WARNING = 0+ALL
ERROR = 0+ALL
CRITICAL = 0+ALL

ALLY = 1
ENEMY = 2

ALL_TROOPS = [1,2,3,4,5,6,7]
FREE_TROOPS = 1
REINFORCING_TROOPS = 2
FORCASTING_TROOPS = 3
DEFENDING_TROOPS = 4
ATTACKING_TROOPS = 5
ALLIED_REINFORCEMENTS = 6
MOVING_TROOPS = 7


LOG_FILENAME = 'War.log'
if DEBUG or INFO or WARNING or ERROR or CRITICAL: 
  logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, filemode='w')



def neutral_entry_compare(entry1, entry2):
    return cmp(entry1[1], entry2[1])