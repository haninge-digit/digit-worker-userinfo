import httpx
import os
# import traceback

# from zeebe_worker import WorkerError

USERINFOCASH = os.getenv('USERINFOCASH',"userinfocash.worker-services:8080") # This is the default

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
        if taskvars['_HTTP_METHOD'] != "GET":
            return {'_DIGIT_ERROR':"Only GET method is supported at the moment"}
        if 'userid' not in taskvars:
            return {'_DIGIT_ERROR':"Missing mandatory variable 'userid'"}
        if taskvars['userid'] == "":        # Not allowed!
            return {'_DIGIT_ERROR':"Anonymous users are not allowed to request user info"}
        userID = taskvars['personal_number'] if 'personal_number' in taskvars and taskvars['personal_number']!= "" else taskvars['userid']   # This might need to have restrictions?
        userID = self.normpnum(userID)

        args = {}
        if '_NO_UPDATE' in taskvars:
            args['_NO_UPDATE'] = ""
        if '_NO_CASH' in taskvars:
            args['_NO_CASH'] = ""

        async with httpx.AsyncClient(timeout=10, verify=False) as client:
            r = await client.get(f"http://{USERINFOCASH}/userinfo/{userID}", params=args)
            if r.status_code != 200:
                return {'_DIGIT_ERROR': r.text, '_DIGIT_ERROR_STATUS_CODE': r.status_code}       # Error from userinfocash service

        userinfo = r.json()
        user = {}   # user values to return
        user['person_id'] = userinfo['PersonId'].strip()
        if ',' in userinfo['GivenName']:
            user['first_name'] = userinfo['GivenName'].split(',')[1].strip()    # Get first (given) name from last part of 'GivenName'
        else:
            user['first_name'] = userinfo['GivenName'].strip()      # Just grab what is there
        user['last_name'] = userinfo['LastName'].strip()
        user['full_name'] = userinfo['FirstName'].strip()+" "+userinfo['LastName'].strip()
        user['address'] = userinfo['Address'].strip()
        user['zipcode'] = userinfo['ZipCode'].strip()
        user['city'] = userinfo['City'].strip()
        # user['country'] = userinfo['Country'].strip()       # Skip this for now
        user['municipality_code'] = userinfo['MunicipalityCode'].strip()
        for k,v in userinfo.items():
            if k not in ['PersonId','Address','BirthPlace','City','CivilStatus','Country','FirstName','GivenName','LastName','ZipCode','MunicipalityCode','Parish','Relation']: # List of KIR data
                user[k] = v     # Added extra data that are not from KIR

        return {'user': user}     # Return what we found
        # return user     # Return what we found
