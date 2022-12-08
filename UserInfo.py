import httpx
import os
import json
import logging

from zeebe_worker import WorkerError


USERINFOCASH = os.getenv('USERINFOCASH',"userinfocash:8080") # This is the default

class UserInfo(object):

    queue_name = "userinfo"

    def __init__(self):
        pass


    def normpnum(self, pnum):     # This function is a quick fix and needs rework!
        pnum = pnum.replace('-','')
        if pnum.isdigit():
            if len(pnum) == 10:
                pnum = "19"+pnum if int(pnum[:2]) > 22 else "20"+pnum
            if len(pnum) == 12:
                return pnum
        return(pnum)

    async def worker(self, taskvars):
        stand_alone = '_STANDALONE' in taskvars

        if 'userid' not in taskvars or taskvars['userid'] == "":
            logging.error(f"Call is missing mandatory variable 'userid'")
            return self._handle_worker_error(stand_alone, "Missing mandatory variable 'userid'")
        userID = taskvars['personal_number'] if 'personal_number' in taskvars and taskvars['personal_number'] != "" else taskvars['userid']   # Is this still a valid request?
        userID = self.normpnum(userID)

        logging.debug(f"Running {taskvars['_HTTP_METHOD'] } method for userid {userID}")

        if taskvars['_HTTP_METHOD'] == "GET":
            args = {}
            if '_NO_UPDATE' in taskvars:
                args['_NO_UPDATE'] = ""
            if '_NO_CASH' in taskvars:
                args['_NO_CASH'] = ""

            async with httpx.AsyncClient(timeout=10, verify=False) as client:
                try:
                    r = await client.get(f"http://{USERINFOCASH}/userinfo/{userID}", params=args)
                except httpx.ConnectError:
                    return self._handle_worker_error(stand_alone, f"Couldn't connect to {USERINFOCASH} server")
                if r.status_code != 200:
                    return self._handle_worker_error(stand_alone, f"GET userinfocash returned status code {r.status_code}")

            userinfo = r.json()
            user = {}   # user values to return

            if userID.isdigit():        # Personnummer. External user!
                user['personId'] = userinfo['PersonId'].strip()
                if ',' in userinfo['GivenName']:
                    user['firstName'] = userinfo['GivenName'].split(',')[1].strip()    # Get first (given) name from last part of 'GivenName'
                else:
                    user['firstName'] = userinfo['GivenName'].strip()      # Just grab what is there
                user['lastName'] = userinfo['LastName'].strip()
                user['fullName'] = userinfo['FirstName'].strip()+" "+userinfo['LastName'].strip()
                user['address'] = userinfo['Address'].strip()
                user['zipcode'] = userinfo['ZipCode'].strip()
                user['city'] = userinfo['City'].strip()
                # user['country'] = userinfo['Country'].strip()       # Skip this for now
                user['municipalityCode'] = userinfo['MunicipalityCode'].strip()
                for k,v in userinfo.items():
                    if k not in ['PersonId','Address','BirthPlace','City','CivilStatus','Country','FirstName','GivenName','LastName','ZipCode','MunicipalityCode','Parish','Relation']: # List of KIR data
                        user[k] = v     # Added extra data that are not from KIR
            else:                   # Internal user
                # user = userinfo
                user['firstName'] = userinfo['givenName']
                user['lastName'] = userinfo['surname']
                user['fullName'] = userinfo['displayName']
                user['department'] = userinfo['department']
                user['email'] = userinfo['mail']
                user['managerName'] = userinfo['managerName']

            return {'user': user}     # Return what we found

        elif taskvars['_HTTP_METHOD'] in ["PATCH","POST"]:      # The use of POST here is just until Epi API is updated!!!
            if '_JSON_BODY' not in taskvars:
                return {'_DIGIT_ERROR':"Missing JSON-body in request (nothing to patch)!"}
            patch_data = json.loads(taskvars['_JSON_BODY'])
            async with httpx.AsyncClient(timeout=10, verify=False) as client:
                try:
                    r = await client.patch(f"http://{USERINFOCASH}/userinfo/{userID}", json=patch_data)
                except httpx.ConnectError:
                    return self._handle_worker_error(stand_alone, f"Couldn't connect to {USERINFOCASH} server")
                if r.status_code != 200:
                    return self._handle_worker_error(stand_alone, f"PATCH userinfocash returned status code {r.status_code}")
            return {}

        elif taskvars['_HTTP_METHOD'] == "DELETE":      # The caller wants to delete cash data
            async with httpx.AsyncClient(timeout=10, verify=False) as client:
                try:
                    r = await client.delete(f"http://{USERINFOCASH}/userinfo/{userID}")
                except httpx.ConnectError:
                    return self._handle_worker_error(stand_alone, f"Couldn't connect to {USERINFOCASH} server")
                if r.status_code != 200:
                    return self._handle_worker_error(stand_alone, f"DELETE userinfocash returned status code {r.status_code}")
            return {}

        else:
            return self._handle_worker_error(stand_alone, "Only GET, PATCH and DELETE methods are supported.")


    def _handle_worker_error(self,stand_alone,loggtext):
        logging.error(loggtext)
        if stand_alone:
            return {'_DIGIT_ERROR': loggtext}       # This can be returned to the caller
        else:
            raise WorkerError(loggtext, retries=0)          # In a worklfow so cancel further processeing
