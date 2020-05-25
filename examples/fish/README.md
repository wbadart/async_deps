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

To follow along (make sure [`Poetry`][poetry] is installed first):

[poetry]: https://python-poetry.org

```sh
git clone https://github.com/wbadart/async_deps.git \
    && cd async_deps/examples/fish \
    && poetry shell
```

Now, you can train the models:

``sh
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

At this point, read through [`predict.py`](./fish/predict.py) and
[`docker-compose.yml`](./docker-compose.yml). Respectively, they will show you
the "request" and "submit" sides of the async_deps coin. Also check out
[`rabbtimq.svg`](./rabbitmq.svg) to visualize the input queues and output
exchanges configured by `docker-compose.yml`.

You can now spin up the three services:

```sh
docker-compose up
```

Now wait until the service are ready (it'll take a minute to build the
containers the first time). When they're ready, you'll see:

```
...
Creating fish_fish_weight_predictor_1  ... done
Creating fish_fish_length2_predictor_1 ... done
Creating fish_fish_species_predictor_1 ... done
Attaching to fish_fish_length2_predictor_1, fish_fish_weight_predictor_1, fish_fish_species_predictor_1
```

Now visit the `raw` exchange in your RabbitMQ management interface and paste in
one (just one!) of the lines from [`data/sample.ndjson`](./data/sample.ndjson)
into **Publish message**. Set the routing key to `raw` and fire away!

Now click over to the `results` queue and **Get messages**. Behold, the input
data has been filled in with the three predictions!
