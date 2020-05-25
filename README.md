# async_deps

For when your dependencies aren't quite ready yet.

## Usage

First, install the package:

```sh
pip install git+https://github.com/wbadart/async_deps.git
```

Now, in your data-needing coroutines, add a request to the dependency server:

```py
import async_deps

async def my_processor(initial_data):
    extra_data = await async_deps.request(uuid=initial_data["uuid"])
    initial_data.update(extra_data)
    return initial_data
```

Your coroutine `my_processor` will now be awaiting that `extra_data`. In the
meantime, another coroutine can submit data:

```py
import asyncio, json
import async_deps

async def poll_api(seconds):
    while True:
        response = MyAwesomeAPI.fetch("http://coolbeans.com/api?format=json")
        for data in json.loads(response):
            async_deps.submit(data)
        await asyncio.sleep(seconds)
```

Don't forget to schedule the poller!

```py
import asyncio

async def main():
    asyncio.create_task(poll_api(seconds=15))
    process_results = await my_processor(initial_data={"hello": "world"})
    print("Done!", process_results)
    
if __name__ == "__main__":
    asyncio.run(main())
```

Please see the [`examples/`](./examples) directory for more information.
