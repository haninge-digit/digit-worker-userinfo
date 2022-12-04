import os
import logging
import asyncio

from UserInfo import UserInfo


""" 
Environment
"""
ZEEBE_ADDRESS = os.getenv('ZEEBE_ADDRESS',"camunda-zeebe-gateway.camunda-zeebe:26500")
RUN_ZEEBE_LOOP = os.getenv('RUN_ZEEBE_LOOP',"true") == "true"
RUN_HTTP_SERVER = os.getenv('RUN_HTTP_SERVER',"false") == "true"
HTTP_SERVER_PORT = int(os.getenv('HTTP_SERVER_PORT',"8000"))

DEBUG_MODE = os.getenv('DEBUG',"false") == "true"                       # Global DEBUG logging
LOGFORMAT = "%(asctime)s %(funcName)-10s [%(levelname)s] %(message)s"   # Log format


"""
MAIN function (starting point)
"""
async def main():
    # Enable logging. INFO is default. DEBUG if requested
    logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO, format=LOGFORMAT)

    userinfo_worker = UserInfo()           # Create an instance of the worker

    if RUN_HTTP_SERVER:
        from http_server import http_server
        site = await http_server(userinfo_worker, HTTP_SERVER_PORT)        # Create http server

    if RUN_ZEEBE_LOOP:
        from zeebe_worker import worker_loop
        await worker_loop(userinfo_worker, topic="qq1q")       # Create and run Zeebe worker loop
    
    else:
        while True:
            await asyncio.sleep(100*3600)       #   If not polling Zeebe, run until interupted


if __name__ == "__main__":
    asyncio.run(main())
