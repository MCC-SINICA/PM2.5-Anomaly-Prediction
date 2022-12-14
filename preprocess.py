from constants import *
from utils import *
import pandas as pd
import numpy as np
import os, shutil
import json
from tqdm import tqdm
import sys
"""
In the preprocess, it will read origin csv files, parse data and then save
np files what aimed to access data quickly.
"""

opt = parse_version()
print(opt)
feature_cols = ['SO2', 'CO', 'NO', 'NO2', 'NOx', 'O3', 'PM10', 'PM2.5',
                'RAINFALL', 'RH', 'AMB_TEMP', 'WIND_cos', 'WIND_sin',
               ]

# MARK: - Functions
def read_csv(dataset):
    data = pd.DataFrame()
    if dataset == "train":
        st, ed = 0, -1
    elif dataset == "valid":
        st, ed = -1, len(DATASET_FILES)
    elif dataset == "all":
        st, ed = 0, len(DATASET_FILES)
    data_dict = None
    for d in DATASET_FILES[st:ed]:
        read_path = os.path.join("data", d)
        print(read_path)
        data = pd.read_csv(read_path, index_col='Unnamed: 0')
        data = filter_data(data)
        if not data_dict:
            data_dict = data
        else:
            for key in data_dict:
                data_dict[key] = np.concatenate((data_dict[key], data[key])) 
    return data_dict

def filter_data(data):
    # parse real time
    data['read_time'] = pd.to_datetime(data['read_time'])
    # Check whether the site in the sitenames_sorted list 
    data = data[data.sn.isin(SITENAMES)]
    # Sort data by read_time and sitename 
    data = data.sort_values(['read_time', 'sn'])
    # Reorder the data 
    data = data.reset_index(drop=True)
    # Fetch the features from data 
    data_features = data[feature_cols].values
    # Fetch the time feature
    data_day   = np.zeros((data.shape[0], 1))
    data_hour  = np.zeros((data.shape[0], 1))
    data_month = np.zeros((data.shape[0], 1))
    for i, d in enumerate(data['read_time'].apply(lambda x: x.day)):
        data_day[i,] = d
    for i, d in enumerate(data['read_time'].apply(lambda x: x.hour)):
        data_hour[i] = d
    for i, d in enumerate(data['read_time'].apply(lambda x: x.month)):
        data_month[i] = d
    # Append time and extreme event buf into data_features
    data_features = np.concatenate((data_features, data_month, data_day, data_hour), axis=-1)
    # Fetch site and hash
    sn_hash = dict(zip(SITENAMES, range(len(SITENAMES))))
    data_sn = np.zeros((data.shape[0], 1))
    for i, d in enumerate(data['sn']):
        data_sn[i] = sn_hash[d]
    # Split data by sitename
    data_dict = sn_hash.copy()
    data_features = data_features.reshape([-1, len(sn_hash), 16])
    for i, key in enumerate(data_dict):
        data_dict[key] = data_features[:, i, :]
    return data_dict

def get_normalize(data):
    """
        Input: 
            data: dict, data[key] = [time, feature]
        Output:
            mean_dict: dict, mean_dict[key] = [mean]
            std_dict: dict, std_dict[key] = [std]
            threshold_dict: dict, {key: {winter: value, summer: value}}
    """
    mean_dict = {}
    std_dict = {}
    threshold_dict = {}
    thres_dict = {}
    ratio = opt.ratio
    for i, key in enumerate(data):
        _data = data[key].copy()
        thres_list = np.zeros((_data.shape[0], _data.shape[-1]))
        # summer
        s_index = np.isin(_data[:, -3], SUMMER_MONTHS)
        s_mean  = _data[s_index].mean(0)
        s_std   = _data[s_index].std(0)
        s_threshold = s_mean + s_std * ratio
        thres_list[s_index] = s_threshold
        # winter
        w_index = np.isin(_data[:, -3], SUMMER_MONTHS, invert=True)
        w_mean  = _data[w_index].mean(0)
        w_std   = _data[w_index].std(0)
        w_threshold = w_mean + w_std * ratio
        thres_list[w_index] = w_threshold
        # global
        mean = _data.mean(axis=0)
        std  = _data.std(axis=0)

        _data[s_index] /= s_threshold
        _data[w_index] /= w_threshold
        data[key] = _data
        # save 
        mean_dict[key] = mean.tolist()
        std_dict[key] = std.tolist()
        thres_dict[key] = thres_list
        threshold_dict[key] = {"winter": w_threshold, "summer": s_threshold}
    return data, mean_dict, std_dict, thres_dict, threshold_dict 

def put_normalize(data, mean_dict, std_dict, threshold_dict):
    thres_dict = {}
    for i, key in enumerate(data):
        _data = data[key].copy()
        thres_list = np.zeros((_data.shape[0], _data.shape[1]))
        mean = np.array(mean_dict[key])
        std = np.array(std_dict[key])
        # summer
        s_index = np.isin(_data[:, -3], SUMMER_MONTHS)
        s_threshold = threshold_dict[key]["summer"]
        thres_list[s_index] = s_threshold
        # winter
        w_index = np.isin(_data[:, -3], SUMMER_MONTHS, invert=True)
        w_threshold = threshold_dict[key]["winter"]
        thres_list[w_index] = w_threshold
        # normalize
        #_data[:, :7] = (_data[:, :7] - mean[:7]) / std[:7]
        #_data[:, 8:] = (_data[:, 8:] - mean[8:]) / std[8:]
        _data[s_index] /= s_threshold
        _data[w_index] /= w_threshold
        data[key] = _data
        thres_dict[key] = thres_list
    return data, thres_dict

def pm25_to_AQI(x):
    if x<15.5:
        AQI = 0
    elif x<35.5:
        AQI = 1
    elif x<54.5:
        AQI = 2
    elif x<150.5:
        AQI = 3
    elif x<250.5:
        AQI = 4
    elif x<350.5:
        AQI = 5
    else:
        AQI = 6
    return AQI

# MARK: - Main
if __name__ == '__main__':
    # Read data
    print("read data & filter feature")
    print("All...")
    all_data = read_csv("all")
    print("Train...")
    train_data = read_csv("train")
    print("Valid...")
    valid_data = read_csv("valid")

    # Normalize train_data_feature
    print("normalize feature")
    train_norm, train_mean, train_std, train_thres, train_threshold = get_normalize(train_data.copy())
    
    # Concat train tail and valid, and all data
    #for key in train_data:
    #    valid_data[key] = np.concatenate((train_data[key][-opt.memory_size:], valid_data[key]), axis=0)
    # Normalize valid data
    valid_norm, valid_thres = put_normalize(valid_data.copy(), train_mean, train_std, train_threshold)

    # Save file
    print("Save file")
    #data for ratio = 2, data2 for ratio = 1.5

    save_folder = f'data_{opt.ratio}'
    os.makedirs(f"total_dataset/{save_folder}/")
    with open(f"total_dataset/{save_folder}/train_mean.json", "w") as fp:
        json.dump(train_mean, fp, ensure_ascii=False, indent=4)
    with open(f"total_dataset/{save_folder}/train_std.json", "w") as fp:
        json.dump(train_std,  fp, ensure_ascii=False, indent=4)
    with open(f"total_dataset/{save_folder}/train_threshold.json", "w") as fp:
        for key in train_threshold:
            train_threshold[key]["winter"] = train_threshold[key]["winter"].tolist()
            train_threshold[key]["summer"] = train_threshold[key]["summer"].tolist()
        json.dump(train_threshold,  fp, ensure_ascii=False, indent=4)
    
    # check whether the folder exists
    try:
        os.mkdir(f"total_dataset/{save_folder}/origin")
    except:
        shutil.rmtree(f"total_dataset/{save_folder}/origin")
        os.mkdir(f"total_dataset/{save_folder}/origin")
    try:
        os.mkdir(f"total_dataset/{save_folder}/norm")
    except:
        shutil.rmtree(f"total_dataset/{save_folder}/norm")
        os.mkdir(f"total_dataset/{save_folder}/norm")
    try:
        os.mkdir(f"total_dataset/{save_folder}/thres")
    except:
        shutil.rmtree(f"total_dataset/{save_folder}/thres")
        os.mkdir(f"total_dataset/{save_folder}/thres")
    os.mkdir(f"total_dataset/{save_folder}/origin/all")
    os.mkdir(f"total_dataset/{save_folder}/origin/train")
    os.mkdir(f"total_dataset/{save_folder}/origin/valid")
    os.mkdir(f"total_dataset/{save_folder}/norm/train")
    os.mkdir(f"total_dataset/{save_folder}/norm/valid")
    os.mkdir(f"total_dataset/{save_folder}/thres/train")
    os.mkdir(f"total_dataset/{save_folder}/thres/valid")
    
    for key in train_data:
        np.save(f"total_dataset/{save_folder}/origin/all/{key}.npy",   all_data[key])
        np.save(f"total_dataset/{save_folder}/origin/train/{key}.npy", train_data[key])
        np.save(f"total_dataset/{save_folder}/origin/valid/{key}.npy", valid_data[key])
        np.save(f"total_dataset/{save_folder}/norm/train/{key}.npy",   train_norm[key])
        np.save(f"total_dataset/{save_folder}/norm/valid/{key}.npy",   valid_norm[key])
        np.save(f"total_dataset/{save_folder}/thres/train/{key}.npy",  train_thres[key])
        np.save(f"total_dataset/{save_folder}/thres/valid/{key}.npy",  valid_thres[key])
    
