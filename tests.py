import json
import requests
import time
from compare import compare

pass_count = 0
total = 0

#TODO case insensitive json.loads
#TODO pretty print json

def test(req, res):
    global pass_count, total
    time.sleep(1)
    passed = True

    def fail_message(n):
        print 'Test {0} failed'.format(n)
        #print 'Request: '
        #print req
        #print 'Expected Response: '
        #print res
        #print 'Actual Response: '
        #actual = {
        #    "status": r.status_code,
        #    "headers": r.headers,
        #    "content": r.text
        #    }
        #print actual

    def check(expected, actual):
        return expected == actual

    def check_dicts(expected, actual):
        for entry in expected:
            if not entry.lower() in actual:
                return False
            # TODO recursive checking
            if expected[entry] != actual[entry]:
                return False
        return True

    if 'content' in req:
        payload = req['content']
    else:
        payload = {}

    if req['method'] == 'get':
        r = requests.get(req['url'], params=payload)
    elif req['method'] == 'post':
        r = requests.post(req['url'], params=payload)
    elif req['method'] == 'delete':
        r = requests.delete(req['url'], params=payload)

    if 'content-type' in r.headers and r.headers['content-type'] == 'application/json':
        content = json.loads(r.text)
    else:
        content = r.text

    actual = {
        "status": int(r.status_code),
        "headers": r.headers,
        "content": content
    }

    passed = compare(res, actual)

#    if 'status' in res:
#        passed = passed and check(res['status'], int(r.status_code))
#    if 'headers' in res:
#        passed = passed and check_dicts(res['headers'], r.headers)
#
#    if 'content-type' in r.headers and r.headers['content-type'] == 'application/json':
#        passed = passed and check_dicts(res['content'], json.loads(r.text))
#    else:
#        passed = passed and check(res['content'], r.text)

    total += 1
    if passed:
        pass_count += 1
    else:
        fail_message(total)
        print actual

test({
    "url": "http://localhost:4000/http://testsite.com",
    "method": "get"
},
{
    "status": 404,
    "content": "Not Found"
})

test({
    "url": "http://localhost:4000/http://testsite.com",
    "method": "post",
    "content": {
        "content": "<html>hello world</html>"
    }
},
{
    "status": 200,
    "headers": {
        "content-type": "application/json",
        "access-control-allow-origin": "http://testsite.com",
    },
    "content": {
        "message": "successfully created"
    }
})

test({
    "url": "http://localhost:4000/http://testsite.com",
    "method": "delete"
},
{
    "status": 200,
    "headers": {
        "content-type": "application/json",
        "access-control-allow-origin": "http://testsite.com",
    },
    "content": {
        "message": "successfully deleted"
    }
})

#test({
#    "url": "http://localhost:4000/api/v1?action=next-page&hostname=http://somesite.com",
#    "method": "get"
#},
#{
#    "status": 200,
#    "headers": {
#        "content-type": "application/json",
#        "access-control-allow-origin": "*"
#    },
#    "content": {
#        "hostname": "http://somesite.com",
#        "message": "all pages done"
#    }
#})
#
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

print 'passed: ', pass_count
print 'total: ', total
