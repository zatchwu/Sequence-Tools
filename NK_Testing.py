#Zach Wu 2016
#Note: NK Testing does not account for stop codons or deletions

#Adding new models from scikit learn

#Add stipulation for unique mutations?
#(ie: if one site is mutated already, do not mutate again)

import numpy as np
import sys
import random
import NK_Landscape
from scipy.stats import poisson
from scipy.stats import pearsonr
import warnings
import time
from tqdm import tqdm

import warnings
warnings.filterwarnings("ignore")
#warnings.simplefilter('once')

sample_parent = [random.randint(0,19) for i in range(10)]
num_AA = 20

def EPM_Poisson_countd(mu, library_size):
    #returns the Poisson mutation rate distribution for a given library size

    probs_list = []
    mut_list = []
    alpha = 1-1/(library_size*10)
    a,b = poisson.interval(alpha, mu, loc=0)
    a = int(a)
    b = int(b)
    for k in range(a,b+1):
        k_count = int(round(poisson.pmf(k,mu)*library_size,0))
        if k_count != 0:
            probs_list.append(k_count)
            mut_list.append(k)
    dif = sum(probs_list) - library_size
    mutation_list = [i for i in range(a,b+1)]
    index = mutation_list.index(mu)
    probs_list[index] -= dif

    return probs_list, mut_list

def NK_Featurize(seqList):
    featurized_seq = []
    for i, seq in enumerate(seqList):
        temp_seq = [0] * len(seq) * num_AA
        for j, AA in enumerate(seq):
            temp_seq[j*20 + AA] = 1
        featurized_seq.append(temp_seq)
    return featurized_seq

def mutate(p2, n):
    '''mutates parent n times
    '''
    current_seq2 = p2

    for i in range(n):
        #print(current)
        mut_index = random.randint(0,len(p2)-1)
        curr_AA = current_seq2[mut_index]
        poss_AA = set([j for j in range(num_AA)])
        poss_AA.remove(curr_AA)
        mut_AA = list(poss_AA)[random.randint(0,len(poss_AA)-1)]
        current_seq2[mut_index] = mut_AA

    return current_seq2

def epm_library(parent, library_size, rate = 1):
    '''parent sequence should be in [19,3,0,1] format
        rate is the average number of mutations
        I'm just going to assume a poisson distribution for now
        check http://www.ncbi.nlm.nih.gov/pubmed/15939434

        -Fox assumes gamma distribution
    '''
    dist_countL, num_mutL = EPM_Poisson_countd(rate, library_size)

    seq_list = []
    seq_list.append(parent[:])
    for i, num_mut in enumerate(num_mutL):
        for j in range(dist_countL[i]):
            seq_list.append(mutate(parent[:], num_mut)[:])

    return seq_list

def true_epm_library(parent, library_size, rate = 1):
    '''parent sequence should be in [19,3,0,1] format
        rate is the average number of mutations
        -using epm model developed by Sun (1995) and verified by Drummond (2005)
    '''

    dist_countL, num_mutL = true_EPM_countd(rate, library_size)

    seq_list = []
    seq_list.append(parent[:])
    for i, num_mut in enumerate(num_mutL):
        for j in range(dist_countL[i]):
            seq_list.append(mutate(parent[:], num_mut)[:])

    return seq_list

def true_EPM_countd(rate, library_size):
    ''' returns true
    '''

def rand_library(parent, library_size):
    '''parent is included
    '''
    seq_list = []
    seq_list.append(parent)

    for i in range(library_size-1):
        rand_seq = [random.randint(0,num_AA-1) for j in i]
        seq_list.append(rand_seq)

    return seq_list

def single_mutant_library(parent, n):
    ''' sequence should be in [19,3,0,1] format
        n is length of walk
    '''
    current_seq = list(parent)[:]
    seq_list = []
    seq_list.append(parent[:])
    for i in range(n):
        temp = current_seq[:]
        temp = mutate(current_seq, 1)

        current_seq = temp[:]
        seq_list.append(temp)
    return seq_list

###############################################################
###############################################################
###############################################################

#Create Libraries and store energies.

import time
# n = 40              #sequence length
# library_size = 1*n

# beg = time.clock()
# test = NK_Landscape.NKLandscape(n,1, savespace = False, epi_dist = 'gamma')
# interactions_list = test.nk_interactions()
# epistatic_list = test.nk_epistatic()
# end = time.clock()
# print(-beg+end)

# parent = [np.random.randint(num_AA) for i in range(n)]
# print('Parent:' + str(parent))
# library1 = epm_library(parent, library_size, rate=3)
# library2 = single_mutant_library(parent,library_size)
# print('aa')


# library1_features = NK_Featurize(library1)
# library2_features = NK_Featurize(library2)

# library1_fitnessL = []
# library2_fitnessL = []

# # print(interactions_list)
# for i in range(len(library1_features)):
#     t1 = test.get_Energy(library1[i])
#     library1_fitnessL.append(t1)

#     t2 = test.get_Energy(library2[i])
#     library2_fitnessL.append(t2)

###############################################################
###############################################################
###############################################################

#run models
from sklearn.linear_model import *
from sklearn.neighbors import *
from sklearn.neural_network import *
from sklearn.svm import *
from sklearn.tree import *
from sklearn.ensemble import *
from sklearn import cross_validation
from sklearn.cross_decomposition import PLSRegression ##New One
###############################################################

from sklearn.gaussian_process import GaussianProcess
from sklearn.kernel_ridge import KernelRidge



clf_list = [ARDRegression(), BayesianRidge(), ElasticNet(), LassoLarsCV(), LinearRegression(), SGDRegressor(), KNeighborsRegressor(), LinearSVR(), DecisionTreeRegressor(), AdaBoostRegressor(), RandomForestRegressor(), GradientBoostingRegressor(), BaggingRegressor(), KernelRidge(), NuSVR()]
clf_list_notworking = [PLSRegression(n_components = 120), GaussianProcess()]

K_list = [0,1,2,3]
n = 40                    #Sample length = 40
library_size = 3*n        #Library size = 3*n


#whooo
f = open('NK_Model_Testing.txt', 'w')
f2 = open('NK_Model_Correlations.txt','w')

f.write('N = ' + str(n))
f.write('\nLibrary Size = ' + str(library_size) + '\n--------\n')
f2.write('N = ' + str(n))
f2.write('\nLibrary Size = ' + str(library_size) + '\n--------\n')


predict_master_list = []
true_master_list = []


#Write CLF list to file
for i in clf_list:
    print(str(i) + '\n')
    f2.write(str(i) + ', \n')
beg = time.clock()

#Go through different K Values
#REMAKE landscapes, error prone libraries, and corresponding fitnesses
#Train base/default models

for K in K_list:
    print('\n\nK = ' + str(K))

    f.write('\n##########\nNew Fitness Landscape \nK = ' + str(K) + '\n##########\n')
    f2.write('\n\n------\nK Value = ' + str(K) + '\n------\n')


    predict_list_by_clf = []
    true_list_by_clf = []
    #Fit to models and save fitnesses:
    for i, clf in enumerate(clf_list): #!!!!!
        print('Current clf:\n' + str(clf))
        #Save prediction and true lists
        predict_list = []
        true_list = []

        f.write('\nNew CLF, K = ' + str(K) + '\n' + str(clf) + '\n---------\n')
        print('\nProgress Bar: ')
        for j in tqdm(range(200)):

            #Specify parent sequence and library
            parent = [np.random.randint(num_AA) for i in range(n)]
            epm_lib = single_mutant_library(parent, library_size)
            #epm_lib = epm_library(parent, library_size, rate = 3)  # Single Mutants!!
            #Featurize
            lib_features = NK_Featurize(epm_lib)


            #Make NK_Landscape
            landscape = NK_Landscape.NKLandscape(n,K, savespace = False, epi_dist = 'gamma')
            interactions_list = landscape.nk_interactions()
            epistatic_list = landscape.nk_epistatic()

            #Determine Fitnesses
            lib_fitnessL = []
            for i in range(len(lib_features)):
                fitness = landscape.get_Energy(epm_lib[i])
                lib_fitnessL.append(fitness)

            rand_ind = random.randint(0, len(epm_lib)-1)

            #LOO Classification
            X_test, Y_test = [lib_features[rand_ind]], [lib_fitnessL[rand_ind]]
            X_train = lib_features[0:rand_ind] + lib_features[rand_ind+1:]
            Y_train = lib_fitnessL[0:rand_ind] + lib_fitnessL[rand_ind+1:]

            if len(Y_train) != len(set(Y_train)) and clf == GaussianProcess():
                print('GP Error Likely')

                #Hotfix: Remove duplicates by altering one
                while(len(Y_train) != len(set(Y_train))):
                    Y_train_copy = []
                    for ind, Y in enumerate(Y_train):
                        if Y in Y_train_copy:
                            Y_train[ind] = Y-0.00001
                            Y_train_copy.append(Y-0.00001)
                        else:
                            Y_train_copy.append(Y)

            try:
                clf.fit(X_train, Y_train)
                Y_predicted = clf.predict(X_test)
                predict_list.append(Y_predicted[0])
                true_list.append(Y_test[0])

                f.write(str(Y_predicted[0]) + ', ' + str(Y_test[0]) + '\n')

            except np.linalg.linalg.LinAlgError as err:
                print(clf)
                print('failed')

#             except:
#                 if len(Y_train) != len(set(Y_train)):
#                     print('GP Error Likely')

#                     #Hotfix: Remove duplicates by altering one
#                     while(len(Y_train) != len(set(Y_train))):
#                         Y_train_copy = []
#                         for ind, Y in enumerate(Y_train):
#                             if Y in Y_train_copy:
#                                 Y_train[ind] = Y-0.00001
#                                 Y_train_copy.append(Y-0.00001)
#                         else:
#                             Y_train_copy.append(Y)

#                     try:
#                         clf.fit(X_train, Y_train)
#                         Y_predicted = clf.predict(X_test)
#                         predict_list.append(Y_predicted[0])
#                         true_list.append(Y_tescipyt[0])

#                         f.write(str(Y_predicted[0]) + ',' + str(Y_test[0]) + '\n')
#                     except:
#                         print('gg')

#                 else:
#                     print('Unknown error :' + str(sys.exc_info()[0]))


        #Determine Pearson's R
        r = np.corrcoef(predict_list, true_list)
        write_me = 'Rsquared : ' + str(r[0,1]**2) + '\n'
        print(write_me)
        f.write(write_me)
        f2.write(str(r[0,1]**2) + '\n')
        predict_list_by_clf.append(predict_list)
        true_list_by_clf.append(true_list)

    predict_master_list.append(predict_list)
    true_master_list.append(true_list_by_clf)
f.close()
f2.close()
print('end')
print('runtime = ' + str(time.clock() - beg))
