'''
mode_comparator.py
   (BoostSRL-Hacksaw v0.02)
   "Now with 90% more Python!"
   Written by Alexander L. Hayes
   hayesall@indiana.edu
   Last updated: May 10, 2017

Sample Calls:
   $ python mode_comparator.py

Notes:
   - Arrays in 'DATASETS' are the name of the folder, target, and number of features.
'''

from __future__ import print_function
from scipy import stats
from sklearn import cross_validation

#from tabulate import tabulate
from datetime import datetime

import os
import re
import sys

import numpy as np
import matplotlib.pyplot as plt

# https://github.com/google/python-subprocess32
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

EPOCHS = 25
TREES = 10
RDNJARPATH = ' v1-0.jar '
AUCJARPATH = ' -aucJarPath .'

DATASETS = [['Cora', 'sameauthor', 9],
            ['WebKB', 'faculty', 5]]

ALGOS = [['RDN-Boost', '']]

FLAGS = ['tushar', '-e', '-rw', '-w', '-s']

def main():

    for d in DATASETS:

        dataset = d[0]
        target = d[1]
        number_of_features = d[2]

        for a in ALGOS:

            params = a[1]

            for f in FLAGS:
                print(datetime.now().time())
                print(dataset, '| flag:', f)

                training_time_means, training_time_stds = [], []
                roc_means, roc_stds = [], []
                pr_means, pr_stds = [], []
                
                if f in ['-rw', '-w', '-s']:
                    # Random Walk, Walk, or Shortest Walk

                    for n in range(number_of_features):
                        traintime, roc, pr = [], [], []
                        
                        print(dataset, '| # of features:', n + 1, '| flag:', f)
                        
                        for e in range(EPOCHS):
                            
                            # Create the modes file for this Train/Test epoch
                            construct_modes(dataset, f, NUMBER=n)

                            # BoostSRL Training
                            train_model(dataset, params, target)

                            # Find the time (in seconds) from the log file
                            traintime.append(get_training_time())

                            # BoostSRL Testing
                            test_model(dataset, params, target)

                            # Find the AUC ROC and AUC PR
                            roc_score, pr_score = get_roc_and_pr_score()
                            roc.append(roc_score)
                            pr.append(pr_score)
                        
                        # Calculate mean and standard deviation for Training Time, AUC ROC, and AUC PR
                        training_mean, training_std = np.mean(traintime), np.std(traintime)
                        auc_roc_mean, auc_roc_std = np.mean(roc), np.std(roc)
                        auc_pr_mean, auc_pr_std = np.mean(pr), np.std(pr)

                        # Update the arrays holding the values, these will be used for plotting the information
                        training_time_means.append(training_mean)
                        training_time_stds.append(training_std)
                        roc_means.append(auc_roc_mean)
                        roc_stds.append(auc_roc_std)
                        pr_means.append(auc_pr_mean)
                        pr_stds.append(auc_pr_std)
                        
                        '''
                        print_information(training_mean, training_std,
                                          auc_roc_mean, auc_roc_std,
                                          auc_pr_mean, auc_pr_std)
                        '''

                    name_to_save = dataset + '-' + f + '-' + str(EPOCHS) + '.png'

                    plot_errorbars(training_time_means, training_time_stds,
                                   roc_means, roc_stds,
                                   pr_means, pr_stds, name_to_save)
                    log_progress(training_time_means, training_time_stds,
                                 roc_means, roc_stds,
                                 pr_means, pr_stds, name_to_save)
                    #exit()
                    
                else:
                    # for now, do not worry about these while I work on the code for them
                    #continue
                    
                    traintime, roc, pr = [], [], []
                    
                    for e in range(EPOCHS):
                        print(dataset, '| flag:', f, '| epoch:', e)
                        
                        # Create the modes file for this train/test epoch
                        construct_modes(dataset, f)
                        
                        # BoostSRL Training
                        train_model(dataset, params, target)
                        
                        # Find the time (in seconds) from the log file
                        traintime.append(get_training_time())

                        # BoostSRL Testing
                        test_model(dataset, params, target)

                        # Find the AUC ROC and AUC PR
                        roc_score, pr_score = get_roc_and_pr_score()
                        roc.append(roc_score)
                        pr.append(pr_score)

                    name_to_save = dataset + '-' + f + '-' + str(EPOCHS) + '.png'

                    plot_errorbars(traintime, [0] * len(traintime),
                                   roc, [0] * len(roc),
                                   pr, [0] * len(pr), name_to_save)

                    log_progress(traintime, '-', roc, '-', pr, '-', name_to_save)
                    
                    #exit()
                        
                        
def import_data(file_to_read):
    if os.path.isfile(file_to_read):
        with open(file_to_read, 'r') as f:
            data = f.read().splitlines()
        return data
    else:
        raise('Error, there were problems when reading ' + file_to_read)

def data_validation(data):
    #x_train, x_test, y_train, y_test = cross_validation()
    pass

def call_process(call):
    p = subprocess.Popen(call, shell=True)
    os.waitpid(p.pid, 0)

def construct_modes(dataset, flag, NUMBER=None):
    # Extra parameters to Cora Modes (won't work without them):
    if dataset == 'Cora':
        call_process('echo -e "setParam: maxTreeDepth=3.\nsetParam: nodeSize=2." > datasets/Cora/cora_bk.txt')

    # Create the modes file
    if NUMBER is not None:
        CALL = 'python walker2.py --number ' + str(NUMBER) + ' ' + flag + ' diagrams/' + dataset + \
               '.mayukh | grep "mode:" >> datasets/' + dataset + '/' + dataset.lower() + '_bk.txt'
    else:
        if flag == 'tushar':
            CALL = 'cp datasets/' + dataset + '/tushar_' + dataset.lower() + '_bk.txt ' + 'datasets/' + \
                   dataset + '/' + dataset.lower() + '_bk.txt'
        else:
            CALL = 'python walker2.py ' + flag + ' diagrams/' + dataset + \
                   '.mayukh | grep "mode:" >> datasets/' + dataset + '/' + dataset.lower() + '_bk.txt'
    call_process(CALL)

def train_model(dataset, params, target):
    # BoostSRL Training
    CALL = 'java -jar' + RDNJARPATH + '-l -train datasets/' + dataset + '/train/ ' + params + '-target ' + \
           target + ' -trees ' + str(TREES) + ' > trainlog.txt'
    call_process(CALL)

def test_model(dataset, params, target):
    # BoostSRL Testing
    CALL = 'java -jar' + RDNJARPATH + '-i -model datasets/' + dataset + '/train/models/ -test datasets/' + \
           dataset + '/test/ -target ' + target + AUCJARPATH + ' -trees ' + str(TREES) + ' > testlog.txt'
    call_process(CALL)

def get_training_time():
    text = open('trainlog.txt', 'r').read()
    line = re.findall(r'trees\): \d*.\d* seconds', text)
    if not line:
        # Seconds should always be a decimal value, otherwise we need to deal in minutes and seconds
        line = re.findall(r'trees\): \d* minutes and \d*.\d* seconds', text)
        # Convert the minutes into seconds and add the seconds:
        splitline = line[0].split()
        seconds = float(splitline[1] * 60 + float(splitline[4]))
    else:
        seconds = float(line[0].split()[1])
    return seconds

def get_roc_and_pr_score():
    text = open('testlog.txt','r').read()
    line = re.findall(r'AUC ROC   = \d.\d*|AUC PR    = \d.\d*', text)
    roc_score = float(line[0].split()[3])
    pr_score = float(line[1].split()[3])
    return roc_score, pr_score

def print_information(training_mean, training_std, auc_roc_mean, auc_roc_std, auc_pr_mean, auc_pr_std):
    print('Training Time |', training_mean, '+-', training_std)
    print('AUC ROC       |', auc_roc_mean, '+-', auc_roc_std)
    print('AUC PR        |', auc_pr_mean, '+-', auc_pr_std)

def log_progress(training_time_means, training_time_stds, roc_means, roc_stds, pr_means, pr_stds, name_to_save):
    print('Saving information for', name_to_save, 'to file.')
    with open('mode_comp_log.txt', 'a') as f:
        f.write(name_to_save + '\n' + \
                str(training_time_means) + '\n' + str(training_time_stds) + '\n' + \
                str(roc_means) + '\n' + str(roc_stds) + '\n' + \
                str(pr_means) + '\n' + str(pr_stds) + '\n')

def plot_errorbars(training_time_means, training_time_stds, roc_means, roc_stds, pr_means, pr_stds, name_to_save):
    print('Saving image for', name_to_save, 'to "graphs" directory.')
    
    x_axis = range(len(training_time_means)+1)[1:]
    fig, (ax0, ax1, ax2) = plt.subplots(ncols=3, figsize=(15,5))

    # Name at the top
    fig.suptitle(name_to_save)
    
    # ax0: Time
    ax0.errorbar(x_axis, training_time_means, yerr=training_time_stds, fmt='-o')
    ax0.set_xlabel('Number of Steps')
    ax0.set_ylabel('Time')
    ax0.set_title('Training Time')
    ax0.set_xlim([0, len(training_time_means)+1])
    ax0.set_ylim([0, max(training_time_means) + max(training_time_stds) + 1])
    
    # ax1: AUC ROC
    ax1.errorbar(x_axis, roc_means, yerr=roc_stds, fmt='-o')
    ax1.set_xlabel('Number of Steps')
    ax1.set_ylabel('AUC ROC')
    ax1.set_title('AUC ROC')
    ax1.set_xlim([0, len(roc_means)+1])
    ax1.set_ylim([0.4,1])
    
    # ax2: AUC PR
    ax2.errorbar(x_axis, pr_means, yerr=pr_stds, fmt='-o')
    ax2.set_xlabel('Number of Steps')
    ax2.set_ylabel('AUC PR')
    ax2.set_title('AUC PR')
    ax2.set_xlim([0, len(pr_means)+1])
    ax2.set_ylim([0.4,1])
    
    plt.savefig('graphs/' + name_to_save, dpi=600)

'''
DATASETS = [['Father', 'father'],
            ['Toy-Cancer', 'cancer'],
            ['WebKB', 'faculty'],
            ['IMDB', 'female_gender'],
            ['Cora', 'sameauthor']]

ALGOS = [['RDN-Boost', ''],
         ['Soft Margin with alpha(0.5) and beta(-2)', '-softm 0.5 -beta -2 '],
         ['Soft Margin with alpha(2) and beta(-10)', '-softm 2 -beta -10 '],
         ['MLN-Boost', '-mln '],
         ['MLN-Boost with -mlnClause', '-mln -mlnClause '],
         ['LSTree Boosting Regression', '-reg ']]
'''

'''
from __future__ import print_function
from scipy import stats
from tabulate import tabulate
import numpy as np

# Tushar Scores for Learning Time (s), Inference Time (s), AUC ROC Score (.../1.0), AUC PR Score (.../1.0)
tusharlearning = [50.478,53.559,51.199,51.647,51.905,54.063,53.503,53.205,50.436,52.368,52.660,52.340,51.432,53.686,50.264,50.822,50.456,54.750,55.617,50.250,53.459,50.006,54.784,51.240,50.847]
tusharinference = [2.146,2.254,2.245,2.191,2.015,2.057,2.231,2.262,2.153,2.359,2.206,2.184,2.387,2.221,1.955,2.110,2.202,1.961,2.262,2.216,2.482,2.106,2.102,1.807,2.079]
tusharroc = [0.846560,0.842710,0.841126,0.848733,0.849323,0.845722,0.849106,0.848112,0.845225,0.848702,0.845939,0.846374,0.846343,0.845722,0.846343,0.842368,0.846187,0.848702,0.846498,0.845877,0.846870,0.841747,0.846063,0.846374,0.845038]
tusharpr = [0.975392,0.974795,0.974285,0.975619,0.975816,0.975221,0.975753,0.975645,0.975060,0.975771,0.975214,0.975326,0.975419,0.975221,0.975419,0.974675,0.975285,0.975771,0.975474,0.975278,0.975462,0.974477,0.975344,0.975326,0.975085]

# -e Scores
elearning = [44.861,43.939,42.695,47.721,42.271,45.659,47.668,48.883,43.645,46.782,47.121,44.327,47.161,47.471,43.966,46.215,48.887,46.237,44.489,45.588,43.174,46.081,41.938,46.916,47.952]
einference = [2.175,2.268,2.119,1.989,2.049,2.136,1.965,2.212,2.807,2.193,2.192,1.843,2.137,2.261,1.873,2.211,2.175,2.062,2.229,2.215,2.331,2.108,2.280,2.237,2.290]
eroc = [0.850192,0.845939,0.844883,0.849478,0.846063,0.846374,0.848951,0.845628,0.846374,0.848702,0.845722,0.845318,0.845784,0.846063,0.846684,0.846094,0.842368,0.846467,0.845722,0.846808,0.846125,0.848205,0.846467,0.846187,0.845970]
epr = [0.976101,0.975276,0.974840,0.975872,0.975344,0.975326,0.975861,0.975187,0.975379,0.975771,0.975221,0.975004,0.975252,0.975344,0.975539,0.975251,0.974675,0.975359,0.975221,0.975479,0.975345,0.975680,0.975458,0.975384,0.975311]

# -r Scores
rlearning = [45.128,42.980,38.521,45.642,44.830,44.687,45.939,41.365,41.439,42.864,44.277,46.574,34.099,43.448,41.702,39.384,47.706,39.160,47.385,39.736,45.316,46.320,37.389,39.068,43.956]
rinference = [2.292,2.158,2.105,2.321,2.011,1.881,2.233,2.308,2.288,2.150,2.248,2.182,2.374,2.024,2.314,2.011,2.251,2.202,2.206,2.156,1.925,2.243,2.214,2.312,2.027]
rroc = [0.846249,0.850161,0.850099,0.849540,0.849323,0.846249,0.845535,0.846343,0.848795,0.845722,0.846591,0.842710,0.848671,0.849665,0.845597,0.849323,0.842306,0.846063,0.848547,0.846715,0.845815,0.847926,0.849168,0.845380,0.842058]
rpr = [0.975386,0.976086,0.976069,0.975870,0.975816,0.975386,0.975161,0.975419,0.975805,0.975221,0.975507,0.974795,0.975596,0.975939,0.975154,0.975816,0.974656,0.975344,0.975803,0.975447,0.975255,0.975603,0.975780,0.975117,0.974580]

# -w Scores
wlearning = [38.545,39.984,38.079,38.719,38.504,36.822,38.382,38.185,38.682,40.712,39.530,38.046,44.618,39.899,42.313,40.428,42.508,38.283,39.605,39.206,37.877,37.959,38.666,39.130,37.371]
winference = [2.268,1.931,2.241,2.284,1.948,1.959,2.570,2.330,2.139,2.185,2.234,1.939,2.234,2.174,1.985,2.130,2.366,2.267,2.144,1.901,2.281,2.288,2.378,2.232,2.032]
wroc = [0.846622,0.848609,0.850099,0.849634,0.849944,0.846343,0.845877,0.846963,0.849013,0.849230,0.849385,0.848702,0.846467,0.849572,0.846715,0.848920,0.849665,0.851279,0.845628,0.842710,0.842430,0.849044,0.845628,0.845628,0.845877]
wpr = [0.975414,0.975736,0.976069,0.975905,0.976014,0.975323,0.975252,0.975495,0.975781,0.975781,0.975847,0.975771,0.975359,0.975906,0.975405,0.975713,0.975939,0.976338,0.975187,0.974795,0.974704,0.975894,0.975187,0.975187,0.975278]

# -s Scores
slearning = [31.726,30.756,30.280,33.033,30.395,32.226,31.241,31.520,30.464,31.100,31.400,32.705,34.701,31.517,31.723,33.472,31.887,31.767,32.049,32.702,31.562,33.203,31.134,33.563,32.867]
sinference = [2.312,1.861,2.381,2.006,1.914,2.174,2.225,2.184,2.135,2.136,2.051,1.906,2.274,2.105,2.186,1.832,2.152,2.156,2.189,2.169,2.605,2.074,2.346,2.080,2.218]
sroc = [0.843114,0.846622,0.849478,0.842617,0.844945,0.845815,0.842058,0.846808,0.847802,0.845722,0.842617,0.846560,0.845722,0.846498,0.846560,0.846405,0.846094,0.848702,0.841654,0.845815,0.846374,0.849230,0.846218,0.851497,0.846467]
spr = [0.974721,0.975414,0.975872,0.974762,0.974874,0.975255,0.974566,0.975479,0.975677,0.975221,0.974762,0.975492,0.975221,0.975474,0.975392,0.975341,0.975342,0.975668,0.974442,0.975255,0.975326,0.975781,0.975381,0.976219,0.975359]

learning_stat_sig = stats.f_oneway(tusharlearning, elearning, rlearning, wlearning, slearning)
inference_stat_sig = stats.f_oneway(tusharinference, einference, rinference, winference, sinference)
roc_stat_sig = stats.f_oneway(tusharroc, eroc, rroc, wroc, sroc)
pr_stat_sig = stats.f_oneway(tusharpr, epr, rpr, wpr, spr)

print('\nPart I: Cora Dataset with RDN-Boost\n')
print(tabulate([['Exhaustive', 
                 str(str(round(np.mean(tusharlearning), 2)) + ' + ' + str(round(np.std(tusharlearning), 2))),
                 str(str(round(np.mean(tusharinference), 2)) + ' + ' + str(round(np.std(tusharinference), 2))),
                 str(str(round(np.mean(tusharroc), 2)) + ' + ' + str(round(np.std(tusharroc), 4))),
                 str(str(round(np.mean(tusharpr), 2)) + ' + ' + str(round(np.std(tusharpr), 5)))],
                ['All',
                 str(str(round(np.mean(elearning), 2)) + ' + ' + str(round(np.std(elearning), 2))),
                 str(str(round(np.mean(einference), 2)) + ' + ' + str(round(np.std(einference), 2))),
                 str(str(round(np.mean(eroc), 2)) + ' + ' + str(round(np.std(eroc), 4))),
                 str(str(round(np.mean(epr), 2)) + ' + ' + str(round(np.std(epr), 5)))],
                ['Random',
                 str(str(round(np.mean(rlearning), 2)) + ' + ' + str(round(np.std(rlearning), 2))),
                 str(str(round(np.mean(rinference), 2)) + ' + ' + str(round(np.std(rinference), 2))),
                 str(str(round(np.mean(rroc), 2)) + ' + ' + str(round(np.std(rroc), 4))),
                 str(str(round(np.mean(rpr), 2)) + ' + ' + str(round(np.std(rpr), 5)))],
                ['Walk',
                 str(str(round(np.mean(wlearning), 2)) + ' + ' + str(round(np.std(wlearning), 2))),
                 str(str(round(np.mean(winference), 2)) + ' + ' + str(round(np.std(winference), 2))),
                 str(str(round(np.mean(wroc), 2)) + ' + ' + str(round(np.std(wroc), 4))),
                 str(str(round(np.mean(wpr), 2)) + ' + ' + str(round(np.std(wpr), 5)))],
                ['Shortest',
                 str(str(round(np.mean(slearning), 2)) + ' + ' + str(round(np.std(slearning), 2))),
                 str(str(round(np.mean(sinference), 2)) + ' + ' + str(round(np.std(sinference), 2))),
                 str(str(round(np.mean(sroc), 2)) + ' + ' + str(round(np.std(sroc), 4))),
                 str(str(round(np.mean(spr), 2)) + ' + ' + str(round(np.std(spr), 5)))],
                ['pvalues (ANOVA)',
                 str(learning_stat_sig[1]),
                 #'-',
                 str(inference_stat_sig[1]),
                 #'-',
                 str(round(roc_stat_sig[1], 4)),
                 str(round(pr_stat_sig[1], 4))]],
               headers=['Method', 'Training (s)', 'Testing (s)', 'AUC ROC', 'AUC PR'],
               tablefmt='latex'))
#tablefmt='latex'
#tablefmt='orgtbl'

'''

if __name__ == '__main__': main()
