# async_deps

[![CI](https://github.com/wbadart/async_deps/workflows/CI/badge.svg)][ci]

[ci]: https://github.com/wbadart/async_deps/actions?query=workflow%3ACI

For when your dependencies aren't quite ready yet.

## Usage

First, install the package:

```sh
pip install git+https://github.com/wbadart/async_deps.git
```

Now request the data you need:

```py
from async_deps import Cache

cache = Cache("name", "occupation")

async def my_processor(message):
    extra_data = await cache.request(name="bob", occupation="builder")
    extra_data.update({"greeting": message})
    return extra_data
```

`async_deps.request` takes a collection of keyword arguments to match against
submitted data. In this example, we'll receive the first submitted object with
`obj["name"] == "bob"` and `obj["occupation"] == "builder"`. In less contrived
cases, the query will probably be based on the arguments to the coroutine.

Your coroutine `my_processor` will now be awaiting that `extra_data`. In the
meantime, another coroutine can submit data:

```py
import asyncio, json

async def poll_api(seconds):
    while True:
        response = MyAwesomeAPI.fetch("http://coolbeans.com/api?format=json")
        cache.submit(response)
        await asyncio.sleep(seconds)
```

Don't forget to schedule the poller! (And please note: polling represents what
is probably the simplest possible approach to submission. You have the full
power of [`asyncio`][aio] behind you to create much more sophisticated
solutions!)

[aio]: https://docs.python.org/3/library/asyncio.html

```py
import asyncio

async def main():
    asyncio.create_task(poll_api(seconds=15))
    results = await my_processor(message="hola")
    print("Done!", results)
    
if __name__ == "__main__":
    asyncio.run(main())
```

Please see the [`examples/`](./examples) directory for more information.
