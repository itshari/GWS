#!/usr/bin/env python

from pymongo import MongoClient
from gwsconfig import gwsconf
import sys, string, random, datetime, pytz, json

db_client = MongoClient()
db = db_client[gwsconf['graple_db_name']]
collection = db[gwsconf['api_coll_name']]
expcoll = db[gwsconf['graple_coll_name']]

def api_keygen(size = 64, chars = string.ascii_uppercase + string.digits):
    random.seed()
    bid = ''.join(random.choice(chars) for _ in range(size))
    while collection.find_one({'key':bid}) != None:
        bid = ''.join(random.choice(chars) for _ in range(size))
    return bid

if len(sys.argv) == 1:
    print 'Usage:'
    print 'drop'
    print 'insertdef'
    print 'insert name email tz'
    print 'delete email'
    print 'query email'
    print 'print'
    print 'debug on/off email'
    print 'export filename'
    print 'import filename'
    print 'dropexp'
    sys.exit()

operation = sys.argv[1]

# format = {
# 'key': char stream of length 64
# 'name': name of the user
# 'email': default email address of the user
# 'tz': timezone for emails 
# 'debug': whether to include logs with results
# }

if operation == 'drop':
    collection.drop()
    print "Dropped the API key collection"
elif operation == 'dropexp':
    expcoll.drop()
    print "Dropped the Experiment collection"
elif operation == 'insertdef':
    insdoc = {'key': '0' ,'name':'Graple User', 'email':'', 'tz':'US/Eastern', 'debug':False}
    if insdoc['tz'] in pytz.all_timezones:
        print "Inserted at ID:", collection.insert_one(insdoc).inserted_id
    else:
        print "Timezone not found. Closest matches:"
        for tzitem in pytz.all_timezones:
            if insdoc['tz'] in tzitem:
                print tzitem
elif operation == 'insert':
    # Setting the default value for debug as False while creating a user, it could be modified using the command line option - debug
    insdoc = {'key': api_keygen(),'name':sys.argv[2], 'email':sys.argv[3], 'tz':sys.argv[4], 'debug':False} 
    if insdoc['tz'] in pytz.all_timezones:
        print "Inserted at ID:", collection.insert_one(insdoc).inserted_id
    else:
        print "Timezone not found. Closest matches:"
        for tzitem in pytz.all_timezones:
            if insdoc['tz'] in tzitem:
                print tzitem
elif operation == 'delete':
    print "Found:", collection.find_one({'email':sys.argv[2]})
    print "Delete count:", collection.delete_one({'email':sys.argv[2]}).raw_result['n']
elif operation == 'query':
    print collection.find_one({'email':sys.argv[2]})
elif operation == 'debug':
    print 'Modified:', collection.update_one({'email':sys.argv[3]}, {'$set':{'debug': True if sys.argv[2] == 'on' else False}}).modified_count
elif operation == 'print':
    for doc in collection.find({}):
        print doc
elif operation == 'export':
    with open(sys.argv[2], 'w') as ff:
        json.dump(list(collection.find({}, {'_id':False})), ff)
elif operation == 'import':
    with open(sys.argv[2], 'r') as ff:
        insdoc = json.load(ff)
    print "Inserted at ID:", collection.insert_many(insdoc).inserted_ids
