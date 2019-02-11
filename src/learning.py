import datetime as dtm

import numpy as np
from scipy import stats
from sklearn import ensemble
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV

from src.data_preparator import prepare_data

if __name__ == '__main__':
    x_train, y_train = prepare_data('AAPL', dtm.datetime(2016, 1, 1), dtm.datetime(2018, 1, 1))
    x_test, y_test = prepare_data('AAPL', dtm.datetime(2018, 1, 1), dtm.datetime(2019, 1, 1))

    tuned_parameters = [{'gamma': [1e-3, 1e-4], 'C': [1, 10, 100, 1000]}]
    tuned_parameters_rand = {"C": stats.uniform(2, 10),
                             "gamma": stats.uniform(0.1, 1)}
    scores = ['precision', 'recall']

    print("alright lets go")
    for score in scores:
        print(score)
        # print("SVM")
        # svc = GridSearchCV(svm.SVC(), tuned_parameters, cv=5,
        #                    scoring=score)
        # svc = RandomizedSearchCV(svm.SVC(), tuned_parameters_rand, cv=5, verbose=True, n_iter=1000, scoring=score)
        # svc.fit(x_train, y_train)

        # y_true, y_pred = y_test, svc.predict(x_test)
        # print(classification_report(y_true, y_pred))
        # print(np.sum(y_pred == np.array(y_test)) / len(y_test))

        print("ADA")
        ada_tuned_parameters = [{'n_estimators': np.arange(10, 1000, 15)}]
        svc = GridSearchCV(ensemble.AdaBoostClassifier(), ada_tuned_parameters, cv=5, scoring=score, verbose=True, n_jobs=8)
        svc.fit(x_train, y_train)

        y_true, y_pred = y_test, svc.predict(x_test)
        print(classification_report(y_true, y_pred))
        print(np.sum(y_pred == np.array(y_test)) / len(y_test))
