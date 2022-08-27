import os
import logging
import asyncio

from UserInfo import UserInfo

from zeebe_worker import worker_loop
from http_server import http_server


""" 
Environment
"""
ZEEBE_ADDRESS = os.getenv('ZEEBE_ADDRESS',"camunda-zeebe-gateway.camunda-zeebe:26500")
RUN_ZEEBE_LOOP = os.getenv('RUN_ZEEBE_LOOP',"true") == "true"
RUN_HTTP_SERVER = os.getenv('RUN_HTTP_SERVER',"false") == "true"
HTTP_SERVER_PORT = int(os.getenv('HTTP_SERVER_PORT',"8080"))

DEBUG_MODE = os.getenv('DEBUG',"false") == "true"                       # Global DEBUG logging
LOGFORMAT = "%(asctime)s %(funcName)-10s [%(levelname)s] %(message)s"   # Log format


"""
MAIN function (starting point)
"""
def main():
    # Enable logging. INFO is default. DEBUG if requested
    logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO, format=LOGFORMAT)

    userinfo_worker = UserInfo()           # Create an instance of the worker

    loop = asyncio.new_event_loop()         # And an async loop

    if RUN_ZEEBE_LOOP:
        zeebe_runner = loop.create_task(worker_loop(userinfo_worker))       # Create Zeebe worker loop

    if RUN_HTTP_SERVER:
        http_runner = loop.create_task(http_server(userinfo_worker, HTTP_SERVER_PORT))        # Create http server

    try:
        asyncio.set_event_loop(loop)        # Make the create loop the event loop
        loop.run_forever()                  # And run everything
    except (KeyboardInterrupt):             # Until somebody hits wants to terminate
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()



if __name__ == "__main__":
    main()
