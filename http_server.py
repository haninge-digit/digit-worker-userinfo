import os
import json
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
    query_args['_HTTP_METHOD'] = request.method  # Add method
    if request.can_read_body and request.content_type == 'application/json':
        query_args['_JSON_BODY'] = json.dumps(await request.json())

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
