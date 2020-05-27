This directory is a little Python package of models about fish. The interesting
thing about our arrangement is that one of the models depends on the
predictions of the other two. That means that in production, if each of these
models is a microservice, that third model needs a way to gather the results of
the other two.

Specifically, we've got a dataset [from Kaggle][dataset] about fish.
Ultimately, we're going to predict the species of a fish. The _catch_ is that
our users don't know the `Weight` or `Length2` features &mdash; which our
species predictor needs &mdash; so we need two extra models to fill those in.

[dataset]: https://www.kaggle.com/aungpyaeap/fish-market

To follow along (make sure [`poetry`][poetry] is installed first):

[poetry]: https://python-poetry.org

```sh
git clone https://github.com/wbadart/async_deps.git \
    && cd async_deps/examples/fish \
    && poetry shell \
    && poetry install
```

Now you can train the models:

```sh
python -m fish.train
```

The output of this script is a classification report for the species
classifier, and the last two numbers are the explained variance of the two
"fill-in" models. You'll see a `.joblib` file for each of the three trained
models:

```sh
$ ls *.joblib
length2.joblib species.joblib weight.joblib
```

At this point, read through [`fish/predict.py`](./fish/predict.py) and
[`docker-compose.yml`](./docker-compose.yml). Respectively, they will show you
the "request" and "submit" sides of the async_deps coin. Also check out
[`config/queues.svg`](./config/queues.svg) to visualize the input queues and
output exchanges configured by `docker-compose.yml`.

You can now spin up the three services:

```sh
docker-compose up
```

Don't be alarmed by the predictor services repeatedly failing; they'll connect
just fine when the RabbitMQ server finishes spinning up (in fact, you'll be
able to see them authenticate in the `rabbitmq_1` logs; that's your sign the
system is ready).

Now visit the [`raw` exchange][raw] in your RabbitMQ management interface
(username `guest`, password `guest`) and paste any line (just one!) from
[`data/sample.ndjson`](./data/sample.ndjson) into the **Publish message**
payload. Set the routing key to `raw` and fire away!

[raw]: http://localhost:15672/#/exchanges/%2F/raw

```json
{"Length1":15,"Length3":17.2,"Height":4.5924,"Width":2.6316,"ID":0}
```

Now click over to the [`results` queue][results] and **Get messages**. Behold,
the input data has been filled in with the three predictions!

[results]: http://localhost:15672/#/queues/%2F/results

```json
{"ID":0,"Length1":15,"Length3":17.2,"Height":4.5924,"Width":2.6316,"Weight":51.5,"Length2":16.2,"Species":"Bream"}
```
