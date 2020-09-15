"""async_deps/cache.py

Exports `Cache`, a class for managing incoming data and asynchronously
dispatching that data to clients who request it.

created: MAY 2020
"""

import asyncio
import inspect
import operator as op
from functools import wraps
from warnings import warn

__all__ = ["Cache", "_"]


class Cache:
    """Manage incoming data and asynchronously dispatch it to clients."""

    def __init__(self, index_on, cache=None):
        """Initialize a cache for querying the fields listed in `index_on`."""
        self._index_on = set(index_on)
        self._cache = cache if cache is not None else {}
        self._unfulfilled_requests = {}

    async def request(self, **query):
        """An awaitable that will resolve with the first submission matching `query`.

        Each keyword argument should name a field in `index_on` and give the
        desired matching value to look for in submissions. For example:

        >>> my_cache = Cache(index_on=["name", "occupation"])
        >>> result = await my_cache.request(name="bob", occupation="builder")
        >>> assert result["name"] == "bob" and result["occupation"] == "builder"
        """
        self._check_query(query)
        index = frozenset(query.values())
        if index in self._cache:
            return self._cache.pop(index)
        else:
            response = asyncio.Future()
            self._unfulfilled_requests[index] = response
            return await response

    def submit(self, obj):
        """Submit an object to the cache if it has all the fields in `index_on`."""
        try:
            index = frozenset(obj[key] for key in self._index_on)
        except KeyError as key:
            warn(f"Submission {obj} was missing index key {key}. Discarding...")
            return
        if index in self._unfulfilled_requests:
            response = self._unfulfilled_requests.pop(index)
            response.set_result(obj)
        else:
            self._cache[index] = obj

    def inject(self, **queries):
        """A decorator which supplies request results as args to the decorated function.

        Each keyword argument to the decorator should name an argument to the
        decorated function and give the desired query. Only the first argument
        cannot be injected; this is to support placeholder queries for when
        subsequent arguments depend on the first. For example:

        >>> my_cache = Cache(index_on=["company_id"])
        >>> @my_cache.inject(employer={"company_id": _["employer_company_id"]})
        ... def employee_data(user, employer):
        ...     # ...

        In the `employee_data` body, `employer` will be the submission whose
        `company_id` field matched the `user`'s `employer_company_id` field.
        Note, the decorated function will become a coroutine.
        """
        for query in queries.values():
            self._check_query(query)

        def _decorator(func):
            @wraps(func)
            async def _inner(obj, *args, **kwargs):
                requests = (
                    {k: v(obj) if callable(v) else v for k, v in query.items()}
                    for query in queries.values()
                )
                arg_results = await asyncio.gather(*(self.request(**r) for r in requests))
                result = func(obj, *args, **kwargs, **dict(zip(queries, arg_results)))
                if inspect.isawaitable(result):
                    result = await result
                return result

            return _inner

        return _decorator

    def _check_query(self, query):
        if set(query) != self._index_on:
            raise ValueError(
                "You requested something I'm not indexing on "
                f"(query{set(query)} != index_on{self._index_on})"
            )


class _DeferredItemAccess:
    # pylint: disable=too-few-public-methods
    __getitem__ = op.itemgetter


_ = _DeferredItemAccess()
