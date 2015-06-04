import json
import requests
import time

nopassed = 0
total = 0

#TODO case insensitive json.loads
#TODO pretty print json

def test(req, res):
    global nopassed, total
    time.sleep(1)

    def failed():
        print 'Test failed'
        print 'Request: '
        print req
        print 'Expected Response: '
        print res
        print 'Actual Response: '
        print r.status_code
        print r.headers
        print r.text

    def check(expected, actual):
        return expected != actual

    def checkDicts(expected, actual):
        for entry in expected:
            if not entry.lower() in actual:
                failed()
            #TODO
            #if expected[entry] != actual[entry]:
            #    passed = False
        return True

    if req['method'] == 'get':
        r = requests.get(req['url'])
    elif req['method'] == 'post':
        r = requests.post(req['url'])

    check(res['status'], int(r.status_code))
    checkDicts(res['headers'], r.headers)

    if 'content-type' in r.headers and r.headers['content-type'] == 'application/json':
        checkDicts(res['content'], json.loads(r.text))
    else:
        check(res['content'], r.text)

    if not failed:
        nopassed += 1
    total += 1

test({
    "url": "http://localhost:4000/api/v1?action=next-page&hostname=http://somesite.com",
    "method": "get"
},
{
    "status": 200,
    "headers": {
        "content-type": "application/json",
        "access-control-allow-origin": "*"
    },
    "content": {
        "hostname": "http://somesite.com",
        "message": "all pages done"
    }
})

#test({
#    "url": "http://localhost:4000/api/v1?action=submit-paths&hostname=http://somesite.com",
#    "method": "post",
#    "content": {
#        "paths": ["/home", "/", "/something"]
#    }
#},
#{
#    "status": 200,
#    "headers": {
#        "content-type": "text/html",
#        "access-control-allow-origin": "*"
#    },
#    "content": {
#        "message": "recieved request"
#    }
#})

print 'passed: ', nopassed
print 'total: ', total
