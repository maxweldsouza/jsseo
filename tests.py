import json
import requests
import time

pass_count = 0
total = 0

#TODO case insensitive json.loads
#TODO pretty print json

def test(req, res):
    global pass_count, total
    time.sleep(1)
    failed = False

    def fail_message():
        failed = True
        print 'Test failed'
        print 'Request: '
        print req
        print 'Expected Response: '
        print res
        print 'Actual Response: '
        print r.status_code
        print r.headers
        print r.text

    def check_helper(expected, actual):
        return expected == actual

    def check_dicts_helper(expected, actual):
        for entry in expected:
            if not entry.lower() in actual:
                return False
            if expected[entry] != actual[entry]:
                return False
        return True

    def check(*args):
        if not check_helper(*args):
            fail_message()

    def check_dicts(*args):
        if not check_dicts_helper(*args):
            fail_message()

    assert(check_dicts_helper({ "key": "value" }, { "key": "value" }))
    assert(not check_dicts_helper({ "key": "value" }, { "key2": "value" }))
    assert(not check_dicts_helper({ "key": "value" }, { "key": "value2" }))

    if req['method'] == 'get':
        r = requests.get(req['url'])
    elif req['method'] == 'post':
        r = requests.post(req['url'])

    check(res['status'], int(r.status_code))
    check_dicts(res['headers'], r.headers)

    if 'content-type' in r.headers and r.headers['content-type'] == 'application/json':
        check_dicts(res['content'], json.loads(r.text))
    else:
        check(res['content'], r.text)

    if not failed:
        pass_count += 1
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

print 'passed: ', pass_count
print 'total: ', total
