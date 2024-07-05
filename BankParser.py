import this
import pandas as pd
import pymupdf
import os
import re
import json

def get_data_sber(trans, ops):
    trans['bank'] = 'sber'
    for op in ops:
        trans['date'].append(op[0])
        trans['time'].append(op[1])
        trans['category'].append(op[2].replace('\n', ': '))
        cost = float(f'{op[4].replace('\xa0', '')}.{op[5]}')
        if op[3] != '+':
            cost *= -1
        trans['cost'].append(cost)
    return trans

def get_data_tink(trans, ops):
    trans['bank'] = 'tink'
    for op in ops:
        trans['date'].append(op[0])
        trans['time'].append(op[1])
        trans['category'].append(op[5])
        cost = float(f'{op[3]}.{op[4]}'.replace(' ',''))
        if op[2] != '+':
            cost *= -1
        trans['cost'].append(cost)
    return trans

def get_data_dir(path, pattern):
    data = pd.DataFrame()
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        
        doc = pymupdf.open(filepath)
        text = '\n'.join([page.get_text() for page in doc])

        ops = re.findall(pattern, text)

        trans = {
            'bank': '',
            'date': [],
            'time': [],
            'cost': [],
            'category': [],
            'filename': [filename]*len(ops)
        }   
        if 'sber' in path:
            trans = get_data_sber(trans, ops)
            pass
        elif 'tink' in path:
            trans = get_data_tink(trans, ops)
        else:
            print('bank doesnt exist')

        temp_data = pd.DataFrame(trans)
        data = pd.concat([data, temp_data])
    return data

def get_data(path, pattern_path):
    with open(pattern_path, 'r') as file:
        patterns = json.load(file)
    data = pd.DataFrame()
    for dirname in os.listdir(path):
        if dirname.split('.')[-1] not in ['ipynb', 'json', 'py']:
            dirpath = os.path.join(path, dirname)
            temp_data = get_data_dir(dirpath, patterns[dirname])
            data = pd.concat([data, temp_data])
    data.reset_index(inplace=True)
    data.drop(['index'], axis=1, inplace=True)
    return data