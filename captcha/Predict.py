# coding=utf-8
from sklearn.svm import SVC
from sklearn import grid_search
import numpy as np
from sklearn import cross_validation as cs
from sklearn.externals import joblib
from CutImage import loadPreidict
import warnings

warnings.filterwarnings("ignore")

PKL = 'captcha.pkl'


def load_data():
    dataset = np.loadtxt('train_data_all.txt', delimiter=',', dtype=str)
    return dataset


# 交叉验证
def cross_validation():
    dataset = load_data()
    row, col = dataset.shape
    X = dataset[:, :col - 1]
    Y = dataset[:, -1]
    clf = SVC(kernel='rbf', C=1000)
    scores = cs.cross_val_score(clf, X, Y, cv=5)
    print("Accuray %0.2f(+/-%0.2f)" % (scores.mean(), scores.std() * 2))


# 模型训练
def train():
    dataset = load_data()
    row, col = dataset.shape
    X = dataset[:, :col - 1]
    Y = dataset[:, -1]
    clf = SVC(kernel='rbf', C=1000)
    clf.fit(X, Y)
    joblib.dump(clf, PKL)


# 识别
def predict(pic_name):
    clf = joblib.load(PKL)
    rs = loadPreidict(pic_name)
    predictValue = []
    for data in rs:
        predictValue.append(clf.predict(data)[0])
    predictValue = [str(i) for i in predictValue]
    # print 'the captcha is:%s' % (''.join(predictValue))
    return ''.join(predictValue)


def search_best_parameter():
    # 高斯核、线性核、poly以及 sgmoid 核函数
    parameters = {'kernel': ('linear', 'poly', 'rbf', 'sigmoid'), 'C': [1, 100]}
    dataset = load_data()
    row, col = dataset.shape
    X = dataset[:, :col - 1]
    Y = dataset[:, -1]
    svr = SVC()
    clf = grid_search.GridSearchCV(svr, parameters)
    clf.fit(X, Y)
    print clf.best_params_

