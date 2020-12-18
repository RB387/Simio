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
    from simio.app.builder import AppBuilder
    builder = AppBuilder(config)
    ```
* Build and run app
    ```python
    app = builder.build_app(config)
    app.run()
    ```
## Handler
Just add `route` decorator to your handler inherited from BaseHandler

If you need custom request validator, you can change handler's property `request_validator_cls`
with your own class that has `AbstractRequestValidator` interface.

You can also change server response on request validation failure with property `on_exception_response`

```python
import trafaret as t

from simio.handler import BaseHandler
from simio.handler.router import route


RequestSchema = t.Dict({
    t.Key("some_number"): t.ToInt(gte=0)
})


@route(path="/v1/hello/{user_id}/")
class ExampleHandler(BaseHandler):
    async def post(self, example: RequestSchema, user_id: int):
        return self.response({"id": user_id, "some_number": example["some_number"],})

    async def get(self, user_id: int):
        return self.response(f"Your id is {user_id}!")

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
Any async function that has `app` argument can be worker 

But for cron `app` should be the only one argument

You can access logger, clients and everything else from app

At this moment supported only async workers/crons, but you can easily create your own director with multiprocessing/multithreading.
Just create class with AbstractDirector interface 
```python
async def ping_worker(app: web.Application, sleep_time: int):
    app.logger.info('Work')
    await asyncio.sleep(sleep_time)


async def cron_job(app: web.Application):
    await app[CLIENTS][MongoClient].db.collection.insert({"status": "alive"})


def get_config():
    return {
        APP: {
            APP.name: "simio_app",
        },
        CLIENTS: {
            MongoClient: {
                "host": "localhost"
            }
        },
        DIRECTORS: {
            AsyncWorkersDirector: {
                ping_worker: {
                    "sleep_time": 5
                },
            },
            AsyncCronsDirector: {
                "*/1 * * * *": (
                    cron_job,
                ),
            },
        },
    }
```

## Clients
To register your client all you need to do is ...  
Ofc! Just add them to config
```python
def get_config():
    return {
        APP: {
            APP.name: "simio_app",
        },
        CLIENTS: {
            MongoClient: {
                "host": "mongodb://localhost:27017"
            }
        },
    }
```
They can be accessed in handler like this:
```python
from simio.handler import BaseHandler
from simio.handler.router import route
from simio.app.config_names import CLIENTS

@route(path="/v1/hello_with_client/{user_id}/")
class HandlerWithClient(BaseHandler):
    @property
    def mongo_client(self):
        return self.app[CLIENTS][MongoClient]

    async def post(self, user_id: int):
        await self.mongo_client.db.coll.insert_one({"user": user_id})
        return self.response({"id": user_id})

```
And that's all!


!! This is 0.x version, so be ready for major updates in minor version !!