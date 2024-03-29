complete_AA_list = ['R','H','K','D','E','S','T','N','Q','C','G','P','A','I', 'L','M','F',\
                    'W','Y','V','*']

comp_AA_dic = dict((j,i) for i,j in enumerate(complete_AA_list))
comp_AA_dic_rev = dict((i,j) for i,j in enumerate(complete_AA_list))


print('start')
import SequenceTools2
import numpy as np
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
import glob
import math

ref = 'CTGGCGAAACAGAAGGGTTGCATGGCTTGCCACGACCTGAAAGCCAAGAAAGTTGGCCCTGCATACGCAGATGTAGCCAAAAAATACGCAGGCCGCAAAGACGCAGTAGATTACCTGGCGGGAAAAATCAAAAAGGGCGGCTCTGGTGTTTGGGGTAGTGTGCCAATGCCACCGCAAAATGTCACCGATGCCGAAGCGAAACAACTGGCACAATGGATTTTATCAATCAAActcgagcaccaccatcaccaccactga'

#4x_NDT2 Plate:
#Note: this section is much longer because it combines sequencing data from both sequencing runs
#Note: if we ever need to combine 3 sequencing runs for the same plate, I will be mildly upset.

#Finding Mutated Indices
file_dir1 = '/Users/ZacharyWu1/Documents/SequenceTools/data/Hth_NDT2_First/*.seq'
#print(list_seq_files)
bpseqL,bpseqStrL,readLengthL,AASeqL,mutIndL, alteredBPs, fileL = SequenceTools2.seqList_from_file(file_dir1, ref = ref)
file_dir2 = '/Users/ZacharyWu1/Documents/SequenceTools/data/Hth_NDT2_Reseq/*.seq'
bpseqL2,bpseqStrL2,readLengthL2,AASeqL2,mutIndL2, alteredBPs2, fileL2 = SequenceTools2.seqList_from_file(file_dir2, ref = ref)

#Using Mutated Indices
mut_indices2 = [41,42,55,58]
bpseqL,bpseqStrL,readLengthL,AASeqL,mutIndL, alteredBPs, fileL = SequenceTools2.seqList_from_file(file_dir1, ref = ref, cutoff = 58, mut_Ind = mut_indices2)
bpseqL2,bpseqStrL2,readLengthL2,AASeqL2,mutIndL2, alteredBPs2, fileL2 = SequenceTools2.seqList_from_file(file_dir2, ref = ref, cutoff = 58, mut_Ind = mut_indices2)

#Combine Two Sequencing Runs
combined_wellID, combined_AASeqL = SequenceTools2.combineSeqData(fileL,AASeqL,fileL2,AASeqL2)
#Generate Mutation List
mutList = SequenceTools2.mutList_NDT(combined_AASeqL, mut_indices2)
#AAFeaturize
sample_features_P2 = SequenceTools2.AAFeaturize(mutList, mut_indices2)
#Read in HPLC Data from Plate 2
fname = 'data/2nd Plate Data (for Import) Averaged.csv'
regr_dat,class_dat = SequenceTools2.getScreeningData(fname)
#Match sequences to HPLC data by well
sample_seqm_P2, regression_dm_P2, class_dm_P2, well_id_list_P2 = SequenceTools2.matchData2WellID(combined_wellID, combined_AASeqL,regr_dat,class_dat)

mutList_P2 = SequenceTools2.mutList_NDT(sample_seqm_P2, mut_indices2)

print('end1')


# for i in range(len(sample_seqm_P2)):
#     for j in range(4):
#         tRange = range(j*21,(j+1)*21+1)
#         section = sample_featuresP2[i][j*21:(j+1)*21+1]
#         print(comp_AA_dic_rev[section.index(1)])
#     print(str(well_id_list_P2[i]) + ' ' + str(sample_seqm_P2[i]) + ' \t' + str(regression_dm_P2[i]) + ',' + str(class_dm_P2[i]) + '\n --')


# test = [''.join(str(i)) for i in well_id_list_P2]

# test1 = []
# for i in test:
#     print(i)
#     if i in test1:
#         print('doubled')
#     test1.append(i)
# print(len(set(test)))

#4x_NDT1 Plate:

#Get sequences from files
file_dir = '/Users/ZacharyWu1/Documents/SequenceTools/data/Hth_NDT1_Edited/*.seq'
bpseqL,bpseqStrL,readLengthL,AASeqL,mutIndL, alteredBPs, fileL = SequenceTools2.seqList_from_file(file_dir, ref = ref)
# for i in AASeqL:
#     print(str(i))

#Mutated residues are: 43,44,57,60
mut_indices1 = [43,44,57,60]
#Rerun with cutoff
bpseqL,bpseqStrL,readLengthL,AASeqL_P1,mutIndL, alteredBPs, fileL_P1 = SequenceTools2.seqList_from_file(file_dir, ref = ref, cutoff = 60, mut_Ind = mut_indices1)
#Generate Mutation List
mutList_P1 = SequenceTools2.mutList_NDT(AASeqL_P1,mut_indices1)
#Feature Representation
sample_features_P1 = SequenceTools2.AAFeaturize(mutList_P1,mut_indices1) #Manual connect?
#Screening Data
fname = 'data/1st Plate Data (for Import) Averaged.csv'
regr_dat, class_dat = SequenceTools2.getScreeningData(fname)
#Match sequence to screening data
sample_seqm_P1, regression_dm_P1, class_dm_P1, well_id_list_P1 = SequenceTools2.matchData2SeqFile(file_dir, [-10,-7], AASeqL_P1, regr_dat, class_dat)
print('end2')

#Now Machine Learning can actually happen.

#Combine 1st and 2nd plates

sample_seqm_features1 = SequenceTools2.AAFeaturize(mutList_P1, mut_indices1)
sample_seqm_features2 = SequenceTools2.AAFeaturize(mutList_P2, mut_indices2)
sample_seqm = sample_seqm_features1 + sample_seqm_features2

mutList = mutList_P1 + mutList_P2

regression_dm = regression_dm_P1 + regression_dm_P2
class_dm = class_dm_P1 + class_dm_P2

temp_wellIDs1 = [i + [1] for i in well_id_list_P1]
temp_wellIDs2 = [i + [2] for i in well_id_list_P2]
well_id_list = temp_wellIDs1 + temp_wellIDs2

#Import sklearn packages
from sklearn.linear_model import *
from sklearn.neighbors import *
from sklearn.neural_network import *
from sklearn.svm import *
from sklearn.tree import *
from sklearn.ensemble import *
from sklearn import cross_validation

X_train, X_test, Y_train, Y_test = cross_validation.train_test_split(sample_seqm, regression_dm, test_size = 1/150)

# clf_list = []

# clf_list.append(ARDRegression().fit(X_train, Y_train))
# clf = BayesianRidge().fit(X_train, Y_train)
# clf = ElasticNet().fit(X_train, Y_train)
# clf = LassoLarsCV().fit(X_train, Y_train)
# clf = LinearRegression().fit(X_train, Y_train)
# clf = SGDRegressor(loss = 'huber').fit(X_train, Y_train)
# clf = KNeighborsRegressor().fit(X_train, Y_train)
# clf = BernoulliRBM().fit(X_train, Y_train)
# clf = LinearSVR().fit(X_train, Y_train)
# #clf = NuSVR.fit(X_train, Y_train)
# clf = DecisionTreeRegressor().fit(X_train, Y_train)
# clf = AdaBoostRegressor().fit(X_train, Y_train)
# clf = RandomForestRegressor().fit(X_train, Y_train)
# clf = GradientBoostingRegressor().fit(X_train, Y_train)
# clf = BaggingRegressor().fit(X_train, Y_train)

#ARDRegression removed


clf_list = [ARDRegression(), BayesianRidge(), ElasticNet(), LassoLarsCV(), LinearRegression(), SGDRegressor(), KNeighborsRegressor(), LinearSVR(), DecisionTreeRegressor(), AdaBoostRegressor(), RandomForestRegressor(), GradientBoostingRegressor(), BaggingRegressor()]
print('aa')

score_list = [0]*len(clf_list)

# for i in range(1,len(sample_seqm)):
#     X_train = sample_seqm[0:i] + sample_seqm[i+1:]
#     Y_train = regression_dm[0:i] + regression_dm[i+1:]
#     X_test =  sample_seqm[i]
#     Y_test = sample_seqm[i]

#     for clf in clf_list:
#         clf.fit(X_train, Y_train)
#         temp = clf.score(X_train, Y_train)

import warnings
warnings.filterwarnings("ignore")                                                                         #!!!!!#

predict_list_by_clf = []
true_list_by_clf = []


for j,clf in enumerate(clf_list):
    clf.fit(sample_seqm, regression_dm)
    score_list[j] += clf.score(sample_seqm, regression_dm)

#score_list_avg = [i/len(clf_list) for i in score_list]
print(score_list)
print('bb')


# This should be a method
# LOO_Regression(clf_list,
for i, clf in enumerate(clf_list):

    predict_list = []
    true_list = []
    for j in range(len(sample_seqm)):
        X_test, Y_test = sample_seqm[j], regression_dm[j]
        X_train = sample_seqm[0:j] + sample_seqm[j+1:]
        Y_train = regression_dm[0:j] + regression_dm[j+1:]

        try:
            clf.fit(X_train, Y_train)
            Y_predicted = clf.predict(X_test)
            predict_list.append(Y_predicted[0])
            true_list.append(Y_test)
        except np.linalg.linalg.LinAlgError as err:
            print(clf)
            print('failed')

    predict_list_by_clf.append(predict_list)
    true_list_by_clf.append(true_list)



#Make a list of models: reorganize accordingly
cycles = 1
#hi = OneVsRestClassifier(LinearSVC(random_state = 0)).fit(X_train, Y_train).predict(X_test)

#for model in model list
incorrect = 0
count1 = 0

# for i in range(len(class_dm)*cycles):
#     X_train, X_test, Y_train, Y_test = cross_validation.train_test_split(sample_seqm,class_dm , test_size = 1/150)
#     #adjust classifier
#     clf = OneVsRestClassifier(ExtraTreesClassifier()).fit(X_train, Y_train).predict(X_test)
#     for j in range(len(clf)):
#         if clf[j] != Y_test[j]:
#             print('Predicted: ' + str(clf[j]) + '  Actual: ' + str(Y_test[j]))
#             incorrect += 1
#         if clf[j] == Y_test[j] and clf[j] == 1:
#             print('Correct Beneficial')
# print('Fraction Correct: ' + str(1 - incorrect/(len(class_dm)*cycles)))
# print(count1)
# try:
#     print(1 - incorrect/count1)
# except ZeroDivisionError:
#     print('Divide by Zero')


# for i in range(len(sample_seqm)):
#     temp = [comp_AA_dic_rev[i] for i in mutList[i]]
#     print("Sample: "  + str(temp))
#     print("Regr  : "  + str(regression_dm[i]) + ' \tClass: ' + str(class_dm[i]) + ' WellID: ' + str(well_id_list[i]))
print('End3')
print(len(class_dm))


