"""async_deps/server.py

The brain of the async_deps operation. Takes requests for data and issues
Futures which will contain the results.

created: MAY 2020
"""

import asyncio
import logging

__all__ = ["request", "submit"]


class DepServer:
    """Cache JSON submissions and asynchronously deliver them to clients."""

    # TODO: size- and time-based cache invalidation options, better data structure
    _cache = []
    _unfulfilled_requests = {}
    _log = logging.getLogger(__name__)

    @classmethod
    async def request(cls, **query):
        """
        A coroutine which will eventually return the first submission to match
        `**query`. `query` specifies the fields and desired values of the input
        data. For example:

        >>> request(uuid="abc123", username="bob")

        will be an awaitable which resolves with the first input data object to
        have `"uuid": "abc123"` and `"username": "bob"`.
        """
        cls._log.info("Got query: %s", query)
        query = tuple(query.items())
        for obj in cls._cache:
            cls._log.debug("Checking cached obj: %s", obj)
            if cls._match(obj, query):
                cls._log.info("Data match! (%s)", obj)
                return obj
        cls._log.info("No matching data yet. Awaiting future...")
        response = asyncio.Future()
        cls._unfulfilled_requests[query] = response
        return await response

    @classmethod
    def submit(cls, obj):
        """
        Cache `obj` and see if any outstanding requests are interested in it.
        """
        cls._log.info("Got submission: %s", obj)
        cls._cache.append(obj)
        for query, response in cls._unfulfilled_requests.items():
            cls._log.debug("Checking query: %s", query)
            if cls._match(obj, query):
                response.set_result(obj)
                cls._log.info("Query match! (%s)", query)
        # TODO: delete filled request somehow w/o cancelling Future
        cls._log.debug("Data handled. Current cache state:\n%s", cls._cache)

    @staticmethod
    def _match(obj, query):
        return all(key in obj and obj[key] == value for key, value in query)


# Aliases for DepServer's public interface
request = DepServer.request  # pylint: disable=invalid-name
submit = DepServer.submit  # pylint: disable=invalid-name
