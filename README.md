# Simio
[![Build Status](https://travis-ci.com/RB387/Simio.svg?branch=main)](https://travis-ci.com/RB387/Simio)  

Small, simple and async python rest api web framework based on aiohttp.
Supports auto swagger generation and background workers. All you need to do is configure config!  

You can see example of application with simio [here](https://github.com/RB387/Simio-app-example).  
## Start with simio:
1. Install simio
    ```
    pip install simio
    ```
2. Start project
    ```
    mkdir my-project && cd my-project
    simio create-app
    >>> Your project name: myproj
    ```

# Tutorial:
Simio is very simple! Here is some examples:
## Run your application
All you need to run your application is:
* Get config
    ```python
    config = get_config()
    ```
* Create app builder
    ```python
    from simio.app import AppBuilder
    builder = AppBuilder(config)
    ```
* Build and run app
    ```python
    app = builder.build_app(config)
    app.run()
    ```
## Handler
Handlers in simio is just functions
Just add `router.handler` decorator to your handler  

Data from request you can mark with `R` type hint. It's path, query and body.  

If you need clients or any variables in your, use type hint such as: `Depends`, `Provide`, `Var`  
This arguments will be auto injected on app startup


If you need custom request validator, you can change `request_validator_cls`
with your own class that has `AbstractRequestValidator` interface.

You can also change server response on request validation failure with argument `on_exception_response`

```python
import trafaret as t

from simio import router, R, web
from simio_di import Depends
from pymongo import MongoClient


RequestSchema = t.Dict({
    t.Key("some_number"): t.ToInt(gte=0)
})


@router.post("/v1/hello/{user_id}/")
async def simple_post_handler(example: R[RequestSchema], user_id: R[int], client: Depends[MongoClient]):
    client.db.coll.insert_one({"status": "alive"})
    return web.json_response({"id": user_id, "some_number": example["some_number"],})

@router.get("/v1/hello/{user_id}/")
async def get(user_id: R[int]):
    return web.json_response(f"Your id is {user_id}!")
```

## Swagger
Just run your app and open:
```
0.0.0.0:8080/api/doc
```
![Example of swagger](https://raw.githubusercontent.com/RB387/Simio/main/git_images/swagger.png)
  
You can find raw json file in your project directory

Swagger generation can be disabled in config

## Workers and Crons
Any async function that has `app` argument can be worker or cron

You can access logger, clients and everything else from app

For client access you can use same syntax for dependency injection

At this moment supported only async workers/crons, but you can easily create your own job executors
Just create class with AbstractExecutor
 
```python
from simio.job import async_worker, async_cron

@async_worker.register()
async def ping_worker(app: web.Application):
    app.logger.info('Work')
    await asyncio.sleep(sleep_time)


@async_cron.register(cron="*/1 * * * *")
async def cron_job(app: web.Application, client: Depends[MongoClient]):
    await client.db.collection.insert({"status": "alive"})
```

## Clients
As we said earlier, simio uses dependency injection, so everything you need to use them is just add type hint
For client configuration use app config
```python
def get_config():
    return {
        AppConfig: {
            AppConfig.name: "simio_app",
        },
        MongoClient: {
            "host": "mongodb://localhost:27017"
        },
    }
```
And that's all!

## Testing
As you see, everything in simio is just a functions, so you can write easy unit tests for them

```python
@router.post('/v1/{user_id}/handle')
async def handler(user_id: R[int], client: Depends[MongoClient]):
    await client.db.coll.insert_one({"user": user_id})
    return web.json_response({"status": "ok"})


async def test_handler():
    result = await handler(1, MagicMock())
    assert ...
```

!! This is 0.x version, so be ready for major updates in minor version !!