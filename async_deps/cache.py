"""async_deps/cache.py

Exports `new_cache`, a function for managing incoming data and asynchronously
dispatching that data to clients who request it.

created: MAY 2020
"""

import asyncio
import logging
from collections import namedtuple
from random import randint

__all__ = ["new_cache"]


def new_cache(*index_on):
    """Return the handles for submitting to and requesting from an async_deps
    cache.

    Paramters
    ---------
    *index_on : Tuple[str]
        Lists the keys you will be querying the cache on. For example,
        initializing the cache with:

        >>> my_cache = new_cache("id", "source")

        enables you to write the query:

        >>> extra_data = await my_cache.request(id="123", source="referrals")

        The keys listed in the request (in the example: "id" and "source") must
        be present in *index_on, and conversely, the request must give a value
        for each key in *index_on (e.g. request(source="foo") without id raise
        a ValueError).

    Returns
    -------
    cache : namedtuple("Cache", "request submit")
        A cache object which you can submit data to and from which you can
        asynchronously request data.

        >>> my_cache.submit({"id": "123", "source": "referrals"})
        >>> my_cache.submit({"id": "456", "source": "direct"})
        >>> await my_cache.request(id="123", source="referrals")
    """
    index_on = set(index_on)
    cache = {}
    unfulfilled_requests = {}
    # Stick a random number on the Logger name to distinguish messages from
    # different caches
    log = logging.getLogger(f"{__name__}.{randint(10, 99)}")

    async def request(**query):
        if set(query) != index_on:
            raise ValueError(
                "You requested something I'm not indexing on "
                f"(query{set(query)} != index_on{index_on})"
            )
        log.debug("Handling request: %s", query)
        index = frozenset(query.values())
        if index in cache:
            log.debug("Cache hit!")
            return cache.pop(index)
        else:
            log.debug("Cache miss :( Awaiting matching submission...")
            response = asyncio.Future()
            unfulfilled_requests[index] = response
            return await response

    def submit(obj):
        try:
            index = frozenset(obj[key] for key in index_on)
        except KeyError as key:
            log.warning(
                "Submission %s was missing index key %s. Discarding...", obj, key
            )
            return
        log.debug("Handling submission: %s", obj)
        if index in unfulfilled_requests:
            log.debug("Matching request!")
            response = unfulfilled_requests.pop(index)
            response.set_result(obj)
        else:
            log.debug("No matching request. Caching...")
            cache[index] = obj

    return namedtuple("Cache", "request submit")(request, submit)
