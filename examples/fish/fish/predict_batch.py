"""examples/fish/fish/predict_batch.py

A batched version of fish/predict.py. Probably more efficient at scale.
created: MAY 2020
"""

import asyncio

import async_deps
import pandas as pd

from fish.predict import COLUMNS, setup_model

# Each batch will be an object with a "batch_id" and "data"
CACHE = async_deps.Cache(index_on=["batch_id", "key"])


def regress(fish_batch, model):
    df = pd.DataFrame.from_records(fish_batch["data"], columns=COLUMNS)
    df["result"] = model.predict(df.drop(columns="ID"))
    return {"batch_id": fish_batch["batch_id"], "data": df.result.to_list()}


async def classify(fish_batch, model):
    batch_id = fish_batch["batch_id"]
    # Using asyncio.gather lets us make both requests concurrently. I could
    # have used it in predict.py, but I wanted to illustrate different
    # patterns.
    weight_batch, length2_batch = await asyncio.gather(
        CACHE.request(batch_id=batch_id, key="weight"),
        CACHE.request(batch_id=batch_id, key="length2"),
    )

    df = pd.DataFrame.from_records(fish_batch["data"], columns=COLUMNS)
    df["Weight"] = weight_batch["data"]
    df["Length2"] = length2_batch["data"]

    df["Species"] = model.predict(df.drop(columns="ID"))
    return {"batch_id": batch_id, "data": df.to_dict(orient="records")}
