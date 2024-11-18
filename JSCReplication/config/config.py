import os
from pathlib import Path

SEED = 42

SQUARE = (7,7)

RECT = (12,7)

BATCH_SIZE = 32

TEST_SIZE = 0.2

CLASS_NAMES = ['BACKGROUND', 'CONCLUSIONS', 'METHODS', 'OBJECTIVE', 'RESULTS']

NUM_CLASSES = len(CLASS_NAMES)


################################# DERIVED ################################


############################### DIRECTORIES ##############################

#
MAIN_DIR = Path(os.path.abspath(__file__)).parent.parent
##
DATASET_DIR = MAIN_DIR.joinpath('datasets')
##
SAVES_DIR = MAIN_DIR.joinpath('saves')
###
MODEL_DIR = SAVES_DIR.joinpath('models')
###
WEIGHTS_DIR = SAVES_DIR.joinpath('weights')
##
CALLBACKS_DIR = MAIN_DIR.joinpath('callbacks')
##
EXPERIMENTS_DIR = MAIN_DIR.joinpath('experiments')
##
CHECKPOINTS_DIR = MAIN_DIR.joinpath('checkpoints')

########################################################################
