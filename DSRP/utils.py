# encoding: utf-8
"""
Author: yen-nan ho
Contact: aaron1aaron2@gmail.com
GitHub: https://github.com/aaron1aaron2
Create Date:  20210907
"""
import os
import argparse
import pandas as pd

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def cache(data, name, switch):
    if switch:
        data.to_pickle(f'output/.cache/{name}.pkl')

def read_cache(name, switch):
    path = f'output/.cache/{name}.pkl'
    if switch:
        try:
            df = pd.read_pickle(path)
            print(f'load cache at {path}')
            return False, df
        except:
            print(f'no cache detect at {path}')
            return True, None
    else:
        return True, None