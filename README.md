# userinfo worker

## General worker design

The userinfo worker follows the normal worker pattern. It's design to funtion in a workflow as well as a standalone component. It listens to the **userinfo** topic.

The function of the worker can be seen as a REST API with a request method (GET, POST, ...), query parameters and an optional JSON-body. When the worker is called through the "/worker/\<worker name\>" URL, this information is passed on to the worker through Zeebe. The worker will take an action, which could result in new data, and return any new data to Zeebe. Which in the case of a single worker, is passed back to the caller (the UI).

If the worker is part of a workflow, i.e., the worker is not the only action in the process, the result is passed on to the next task in the workflow. 

If the worker is called with the "/worker/\<worker name\>" URL, all errors that occur in the worker are passed back to the caller. In the case of a workflow, i.e. a "/workflow/\<workflow ID\>" URL, worker errors will throw an exception to Zeebe and the process will stop.


## Worker function

The userinfo worker retrieves and returns user information. The user can both be an external user identified by a personnummer and an internal user identified by the AD ID. All information is fetched from the userinfo cash service (https://github.com/haninge-digit/digit-service-userinfocash) that handles all retrieval and storage of user information.

The worker also accepts a PATCH method that can be used to update user information.

For more information about how the cash works, see https://github.com/haninge-digit/digit-service-userinfocash.

## API metods

### GET

The GET method retrieves and returns user information. The call only has only one parameter, "userid", which is sent as a query argument in the call. The "userid" parameter is mandatory and an error is raised if not supplied. Note however that the "userid" parameter is set automatically by the Optimizely server when the app is hosted on the server. For more information on this, see https://github.com/haninge-digit/digit-camunda-wrapper#the-userid-parameter. 

The user information returned is contained in an object called "user". The information that is always returned are the fields, "firstName", "lastName" and "fullName". For external users, "personId", "address", "zipcode", "city" and "municipalityCode" is also returned. And for internal users, "department", "email" and "managerName" is returned. This together with any information that is stored with the PATCH command.

The call can take up to ten seconds if the user is not found in the cash.

### PATCH

The PATCH call is used to update the user information with all the values passed in the JSON body in the call. All the values supplied will be returned "as is" in later calls from any UI app. Values that are to be "private" to a certain app should be stored in an object with some app specfic name or prefixed with some app specfic value.

The "userid" parameter is mandatory and an error is raised if it is not supplied.
