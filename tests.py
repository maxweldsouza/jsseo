import json
import requests
import time

pass_count = 0
total = 0

#TODO case insensitive json.loads
#TODO pretty print json

def test(req, res):
    return
    global pass_count, total
    time.sleep(1)
    passed = True

    def fail_message():
        print 'Test failed'
        print 'Request: '
        print req
        print 'Expected Response: '
        print res
        print 'Actual Response: '
        actual = {
            "status": r.status_code,
            "headers": r.headers,
            "content": r.text
            }
        print actual

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

    assert(check(3, 3))
    assert(check(3 + 2, 5))
    assert(check_dicts({ "key": "value" }, { "key": "value" }))
    assert(not check_dicts({ "key": "value" }, { "key2": "value" }))
    assert(not check_dicts({ "key": "value" }, { "key": "value2" }))

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

    if 'status' in res:
        passed = passed and check(res['status'], int(r.status_code))
    if 'headers' in res:
        passed = passed and check_dicts(res['headers'], r.headers)

    if 'content-type' in r.headers and r.headers['content-type'] == 'application/json':
        passed = passed and check_dicts(res['content'], json.loads(r.text))
    else:
        passed = passed and check(res['content'], r.text)

    if passed:
        pass_count += 1
    else:
        fail_message()
    total += 1

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
        "content": {
            "message": "successfully created"
        }
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
        "content": {
            "message": "successfully deleted"
        }
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
