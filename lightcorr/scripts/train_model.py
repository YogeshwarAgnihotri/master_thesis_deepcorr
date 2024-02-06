# Needed to find the other modules. Dont really like this solution.
import sys
import os
sys.path.insert(0, 
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, 
                os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import argparse
import time

from modules.model_training import train_model
from modules.model_validation import perform_validation
from modules.config_utlis import init_model_training
from modules.data_handling import load_prepare_dataset, save_dataset_info
from modules.data_processing import flatten_flow_pairs_and_label
from modules.enviroment_setup import setup_environment
from modules.model_persistence import save_model
from shared.utils import copy_file  

def main():
    """Train a Classifier on the dataset."""
    start_time = time.time()
    parser = argparse.ArgumentParser(
        description='Train a Classifier on the dataset.'
    )
    parser.add_argument(
        '-c', '--config_path', type=str, required=True, 
        help='Path to the configuration file'
    )
    parser.add_argument(
        '-r', '--run_name', type=str, 
        help='Name of the run followed by date time. \
            If not set the current date and time only will be used.'
    )
    args = parser.parse_args()

    config, run_folder_path = setup_environment(args)
    
    print("\nModel type:", config['model_type'])
    print("Selected Model Config:", 
          config['selected_model_configs'])

    copy_file(args.config_path, os.path.join(
        run_folder_path, "used_config_train.yaml"))

    flow_pairs_train, labels_train, flow_pairs_test, labels_test = \
        load_prepare_dataset(config, 
                             run_folder_path)

    flattened_flow_pairs_train, flattened_labels_train = \
        flatten_flow_pairs_and_label(flow_pairs_train, labels_train)

    # Model initialization
    model_type = config['model_type']
    model = init_model_training(config, model_type)

    trained_model = train_model(model, 
                                flattened_flow_pairs_train, 
                                flattened_labels_train)

    perform_validation(trained_model, 
                       flattened_flow_pairs_train, 
                       flattened_labels_train, 
                       config, 
                       run_folder_path)

    save_model(trained_model, run_folder_path)

    save_dataset_info(config, 
                      flow_pairs_train, 
                      labels_train, 
                      flow_pairs_test, 
                      labels_test, 
                      run_folder_path)

    end_time = time.time()
    print(f"\nFull training process finished in {end_time - start_time} seconds.")


if __name__ == "__main__":
    main()