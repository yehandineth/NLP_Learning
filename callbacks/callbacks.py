from config.config import *
from keras.api.callbacks import TensorBoard, ModelCheckpoint

def create_tensorboard_callback(model_name, experiment_name=None, dir_name=EXPERIMENTS_DIR) -> TensorBoard:
    '''
    Create a tensorboard callback.
    Recommended Usage
    Pass in the model name as experiment name.
    '''
    x = os.path.join(dir_name,model_name)
    log_dir = os.path.join(x, experiment_name)
    tensorboard_callback = TensorBoard(log_dir=log_dir, write_images=True)
    print('Saving log files to :', log_dir)
    return tensorboard_callback

def create_model_checkpoint_callback(name: str, directory = CHECKPOINTS_DIR, monitor='val_accuracy') -> ModelCheckpoint:
    '''
    Creates a model checkpoint callback that saves the best model only and only the weights.
    Only mention the name you want for the file the extensions and file paths will be handled properly
    '''
    callback = ModelCheckpoint(directory.joinpath(f'{name}.weights.h5'), save_best_only=True, save_weights_only=True, monitor=monitor, verbose=1)
    return callback