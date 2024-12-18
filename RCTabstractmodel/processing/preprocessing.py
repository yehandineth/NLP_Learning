
import pandas as pd
import pickle
import tf_keras as keras
import tensorflow as tf

from processing.data_handling import file_to_dataframe
from config.config import *

from typing import Dict, Tuple, Any, Self


class Dataset():

    @classmethod
    def create_training_pipeline(cls, dataset_name) -> Self:
        obj = cls('train', dataset_name).adapt()
        with open(SERIALIZATION_DIR.joinpath('text_vocabulary.pkl'), 'wb') as file:
            pickle.dump(obj.text_vectorizer.get_vocabulary(),file)
        with open(SERIALIZATION_DIR.joinpath('char_vocabulary.pkl'), 'wb') as file:
            pickle.dump(obj.char_vectorizer.get_vocabulary(),file)
        return obj.finalize()
    

    @classmethod
    def create_validation_pipeline(cls, dataset_name) -> Self:
        obj = cls('dev', dataset_name)
        with open(SERIALIZATION_DIR.joinpath('text_vocabulary.pkl'), 'rb') as file:
            obj.text_vectorizer = keras.layers.TextVectorization(
                vocabulary=pickle.load(file)

            )
        with open(SERIALIZATION_DIR.joinpath('char_vocabulary.pkl'), 'rb') as file:
            obj.char_vectorizer = keras.layers.TextVectorization(
                vocabulary=pickle.load(file)
            )

        return obj.finalize()
    
    @classmethod
    def create_test_pipeline(cls, dataset_name, ) -> Self:
        obj = cls('test', dataset_name)
        with open(SERIALIZATION_DIR.joinpath('text_vocabulary.pkl'), 'rb') as file:
            obj.text_vectorizer = keras.layers.TextVectorization(
                vocabulary=pickle.load(file)
            )

        with open(SERIALIZATION_DIR.joinpath('char_vocabulary.pkl'), 'rb') as file:
            obj.char_vectorizer = keras.layers.TextVectorization(
                vocabulary=pickle.load(file)
            )

        return obj.finalize()


    def __init__(self, dataset: str, dataset_name: str) -> None:

        self.pipeline = self.prepare_dataset_cache(dataset, dataset_name)
        self.lookup = keras.layers.StringLookup(
            vocabulary=CLASS_NAMES, 
            output_mode='int'
            )
    
        self.text_vectorizer = keras.layers.TextVectorization(
                max_tokens=VOCAB_SIZE,
                output_sequence_length=NUM_TOKENS
            )
        self.char_vectorizer = keras.layers.TextVectorization(
                max_tokens=CHARACTER_VOCAB_SIZE,
                output_sequence_length=CHARACTER_TOKEN_LENGTH
            )
    
    def adapt(self)  -> Self:

        self.text_vectorizer.adapt(self.pipeline.map(lambda features, labels: features['text']))
        self.char_vectorizer.adapt(self.pipeline.map(lambda features, labels: features['chars']))
        return self

    def finalize(self) -> Self:
        self.pipeline = self.pipeline.map(
            map_func=self.vectorize, 
            num_parallel_calls = tf.data.AUTOTUNE, 
            deterministic=True).map(map_func=self.one_hot, 
                                    num_parallel_calls = tf.data.AUTOTUNE, 
                                    deterministic=True
                                    ).prefetch(
                                        buffer_size=tf.data.AUTOTUNE)
        return self

    def split(self, features: Dict[str, Any], labels: Any) -> Tuple[Dict[str, Any], Any]:
        """
        Preprocesses features by converting text to a character-separated representation.

        Args:
            features: Input feature dictionary containing 'text' key
            labels: Corresponding labels for the features

        Returns:
            Modified features dictionary and original labels
        """
        features['chars'] = tf.strings.reduce_join(tf.strings.bytes_split(features['text']), separator=' ', axis=-1)
        return features, labels


    def line_of(self, features: Dict[str, Any], labels: Any) -> Tuple[Dict[str, Any], Any]:
        """
        Adds contextual line position information to feature set.

        Args:
            features: Input feature dictionary with text and line metadata
            labels: Corresponding labels for the features

        Returns:
            Updated features dictionary with `line_of` and original labels
        """

        new_features = {}
        new_features.update({'text' : features['text'], 'chars' : features['chars']})
        new_features['line_of'] = features['line_number'] / features['total_lines']
        return new_features, labels

    def vectorize(self, features: Dict[str, Any], labels: Any) -> Tuple[Dict[str, Any], Any]:
        """
        Converts text and character features to numerical tensor representations.

        Args:
            features: Input feature dictionary with 'chars' and 'text' keys
            labels: Corresponding labels for the features

        Returns:
            Vectorized features dictionary and original labels
        """
        features['chars'] = self.char_vectorizer(features['chars'])
        features['text'] = self.text_vectorizer(features['text'])
        return features, labels

    def prepare_dataset_cache(self, dataset: str, dataset_name: str) -> tf.data.Dataset:
        """
        Prepares and caches a text dataset for machine learning preprocessing.

        Transforms a text file into a cached, preprocessed TensorFlow dataset:
        - Reads dataset from configured path
        - Converts to DataFrame with 'text' as index
        - Saves as CSV in cache directory
        - Creates TensorFlow dataset with preprocessing

        Args:
            dataset: Name of source text file (without .txt extension)
            dataset_key: Configuration key for retrieving dataset path

        Returns:
            Preprocessed TensorFlow dataset with additional feature transformations

        Raises:
            FileNotFoundError: If dataset file is missing
            KeyError: If dataset configuration key is invalid
            IOError: If file reading/writing fails
        """
        file_to_dataframe(
            file_name=DATASET_PATHS[dataset_name].joinpath(f'{dataset}.txt')
            ).set_index(
                keys='text'
            ).to_csv(
                path_or_buf=MAIN_DIR/f'cache/{dataset}.csv'
                )
        dataset : tf.data.Dataset = tf.data.experimental.make_csv_dataset(
                    file_pattern=f'cache/{dataset}.csv',
                    label_name='target',
                    batch_size=BATCH_SIZE,
                    shuffle=False,
                    num_epochs=1
                ) 
        return dataset.map(self.split, num_parallel_calls = tf.data.AUTOTUNE, deterministic=True).map(self.line_of , num_parallel_calls = tf.data.AUTOTUNE, deterministic=True)

    def one_hot(self, features, labels) -> tuple[Dict[str ,Any], Any]:
        """
        Convert categorical labels to one-hot encoded vectors.

        Parameters:
        features : Any
            Input features to be preserved
        labels : Any
            Categorical labels to be one-hot encoded

        Returns:
        Tuple containing original features and one-hot encoded labels
        """
        return features, tf.one_hot(self.lookup(labels)-1, depth=NUM_CLASSES)

    

