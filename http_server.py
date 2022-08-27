import asyncio
import os
import time
import logging

from aiohttp import web, ClientSession, BasicAuth, ClientTimeout, log
from aiohttp.web import HTTPNotFound, HTTPBadRequest, HTTPNotImplemented, HTTPServiceUnavailable, GracefulExit
# aiohttp.log.access_logger

""" 
Environment
"""
DEBUG_MODE = os.getenv('DEBUG','false') == "true"                       # Global DEBUG logging

LOGFORMAT = "%(asctime)s %(funcName)-10s [%(levelname)s] %(message)s"   # Log format


""" 
HTTP handler
"""
async def http_handler(request):
    # logging.info(f"Request for userinfo for {user_id}")

    query_args = dict(request.query)        # Grab all query args
    query_args['HTTP_METHOD'] = request.method  # Add method

    worker = request.app['WORKER']      # Get worker refeence
    resp = await worker(query_args)     # Run the worker
    
    return web.json_response(resp)      # Return the result



async def http_server(worker, port):
    logging.info(f"Starting http-server. Listens on /{worker.queue_name} on port {port}")

    app = web.Application()

    app['WORKER'] = worker.worker

    # Register same handler for all methods
    routes = [
        web.get(f"/{worker.queue_name}", http_handler),
        web.put(f"/{worker.queue_name}", http_handler),
        web.post(f"/{worker.queue_name}", http_handler),
        web.patch(f"/{worker.queue_name}", http_handler),
        web.delete(f"/{worker.queue_name}", http_handler)
    ]
    app.add_routes(routes)

    runner = web.AppRunner(app)

    await runner.setup()
    # site = web.TCPSite(runner, 'localhost', port)
    site = web.TCPSite(runner, port=port)
    await site.start()

    return runner



""" 
This is just for testing
"""
# if __name__ == "__main__":
#     from UserInfo import UserInfo
#     # Enable logging. INFO is default. DEBUG if requested
#     logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO, format=LOGFORMAT)

#     worker = UserInfo()           # Create an instance of the worker

#     # Our web application instance
#     app = web.Application()
#     app['WORKER'] = worker.worker

#     # Register handlers
#     routes = [
#         web.get(f"/{worker.queue_name}", http_handler),
#         web.put(f"/{worker.queue_name}", http_handler),
#         web.post(f"/{worker.queue_name}", http_handler),
#         web.patch(f"/{worker.queue_name}", http_handler),
#         web.delete(f"/{worker.queue_name}", http_handler)
#     ]
#     app.add_routes(routes)

#     # Start the web server!
#     if not DEBUG_MODE:
#         web.run_app(app, access_log=None, print=None)       # Don't be verbose
#     else:
#         web.run_app(app, port=8081)    # Run with defaults




    # loop = asyncio.new_event_loop()
    # http_runner = loop.create_task(http_server(worker))

    # try:
    #     asyncio.set_event_loop(loop)
    #     loop.run_forever()
    # except (KeyboardInterrupt, GracefulExit):  # pragma: no cover
    #     pass
    # finally:
    #     # _cancel_tasks({main_task}, loop)
    #     # _cancel_tasks(all_tasks(loop), loop)
    #     loop.run_until_complete(loop.shutdown_asyncgens())
    #     loop.close()
