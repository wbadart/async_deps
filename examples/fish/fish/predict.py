"""examples/fish/fish/predict.py

Run the fish AI on some input data.
created: MAY 2020
"""

import asyncio
from functools import partial

import async_deps
import joblib
import pandas as pd

# Our users will be submitting data containing these features. Note the absence
# of Weight, Length2, and Species.
COLUMNS = ["ID", "Length1", "Length3", "Height", "Width"]

# ==========
# Initial regressions
# ==========


def regress(fish, model):
    # Put `fish` in a singleton list since we'll be getting one object at a time
    df = pd.DataFrame.from_records([fish], columns=COLUMNS)

    # Our model wasn't trained with the ID column, so it won't know what to do
    # with the extra column if we don't drop it
    df["result"] = model.predict(df.drop(columns="ID"))

    # Analogously to above, calling to_dict on our 1-row data frame will give
    # us a singleton list. Use [0] to unwrap the result from that list
    return df[["ID", "result"]].to_dict(orient="records")[0]


# ==========
# Final classification
# ==========

CACHE = async_deps.Cache(index_on=["ID", "key"])


async def classify(fish, model):
    # Wait until we have the results of the Weight and Length2 predictions; we
    # can't run our classifier without them.
    #
    # When the result is ready, we'll see
    #
    #     weight = {"ID": <same ID as `fish`>, "key": "weight", "result": ???}
    #
    # And a similarly-shaped result for length2.
    weight = await CACHE.request(ID=fish["ID"], key="weight")
    length2 = await CACHE.request(ID=fish["ID"], key="length2")

    # Same story as `regress`: singleton list => 1-row DataFrame
    df = pd.DataFrame.from_records([fish], columns=COLUMNS)
    df["Weight"] = [weight["result"]]
    df["Length2"] = [length2["result"]]

    # $$$$$
    df["Species"] = model.predict(df.drop(columns="ID"))

    return df.to_dict(orient="records")[0]


# ==========
# Misc
# ==========


def setup_model(func, path):
    model = joblib.load(path)
    return partial(func, model=model)
