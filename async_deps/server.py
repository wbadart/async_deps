"""async_deps/server.py

The brain of the async_deps operation. Takes requests for data and issues
Futures which will contain the results.

created: MAY 2020
"""

import asyncio
import json
import sys


class DepServer:
    """Cache JSON data from stdin and asynchronously deliver it to clients."""

    _cache = []  # TODO: size- and time-based cache invalidation options
    _unfulfilled_requests = {}

    @classmethod
    def request(cls, **query):
        """
        Return a Future that resolves with the eventual input data matching
        `query`. `query` specifies the fields and desired values of the input
        data. For example:

        >>> DepServer.request(uuid="abc123", username="bob")

        will be an awaitable which resolves with the first input data object to
        have `"uuid": "abc123"` and `"username": "bob"`.
        """
        query = tuple(query.items())
        response = asyncio.Future()
        for obj in cls._cache:
            if cls._match(obj, query):
                response.set_result(obj)
                break
        else:
            cls._unfulfilled_requests[query] = response
        return response

    @classmethod
    def start_application(cls, main):
        """
        The preferred entry point for DepServer programs. `main` should be a
        coroutine with no arguments that starts the application.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_until_complete(cls.run(loop))
        loop.close()

    @classmethod
    async def run(cls, loop):
        """
        Alternate entry point for DepServer programs. Should be called like:

        >>> loop.run_until_complete(DepServer.run(loop))

        regardless of where your `loop` came from.
        """
        while True:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            cls._on_data(json.loads(line))

    @classmethod
    def _on_data(cls, obj):
        cls._cache.append(obj)
        for query, response in list(cls._unfulfilled_requests.items()):
            if cls._match(obj, query):
                response.set_result(obj)
                del cls._unfulfilled_requests[query]

    @staticmethod
    def _match(obj, query):
        return all(key in obj and obj[key] == value for key, value in query)
