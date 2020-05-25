"""rmq_sklearn/train.py

This highly advanced model represents the pinnacle of machine learning.
created: MAY 2020
"""

from argparse import ArgumentParser

import joblib
import pandas as pd
from sklearn.metrics import classification_report, explained_variance_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


def train(df, target_col, model_cls, metric, model_path):
    target = df.pop(target_col)
    X_train, X_test, y_train, y_test = train_test_split(df, target)

    model = model_cls()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(metric(y_test, y_pred))
    joblib.dump(model, model_path)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "-f", "--file", default="data/fish.csv", help="path to training data"
    )
    args = parser.parse_args()

    df = pd.read_csv(args.file)
    train(
        df, "Species", DecisionTreeClassifier, classification_report, "species.joblib"
    )
    train(
        df.drop(columns="Length2"),  # don't let the model see Length2
        "Weight",
        DecisionTreeRegressor,
        explained_variance_score,
        "weight.joblib",
    )
    train(
        df.drop(columns="Weight"),  # don't let the model see Weight
        "Length2",
        DecisionTreeRegressor,
        explained_variance_score,
        "length2.joblib",
    )


if __name__ == "__main__":
    main()
