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
    time.sleep(0.2)
    passed = True

    def fail_message(n):
        print 'Test {0} failed'.format(n)
        print 'Request:'
        print req

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

    total += 1
    if passed:
        pass_count += 1
    else:
        fail_message(total)
        print actual

# pages
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
    "method": "post"
},
{
    "status": 400
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
    "method": "post",
    "content": {
        "content": "<html>hello world !</html>"
    }
},
{
    "status": 200,
    "headers": {
        "content-type": "application/json",
        "access-control-allow-origin": "http://testsite.com",
    },
    "content": {
        "message": "successfully updated"
    }
})

test({
    "url": "http://localhost:4000/http://testsite.com",
    "method": "get"
},
{
    "status": 200,
    "content": "<html>hello world !</html>"
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

# urls
test({
    "url": "http://localhost:4000/api/v1?action=next-page&hostname=http://testsite.com",
    "method": "get"
},
{
    "status": 200,
    "headers": {
        "content-type": "application/json",
        "access-control-allow-origin": "*"
    },
    "content": {
        "hostname": "http://testsite.com",
        "message": "all pages done"
    }
})

test({
    "url": "http://localhost:4000/api/v1?action=submit-paths&hostname=http://testsite.com",
    "method": "post",
    "content": {
        "paths": "/\n/home"
    }
},
{
    "status": 200,
    "headers": {
        "access-control-allow-origin": "*"
    },
    "content": {
        "message": "recieved request"
    }
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
        "message": "successfully updated"
    }
})

test({
    "url": "http://localhost:4000/http://testsite.com/",
    "method": "get"
},
{
    "status": 200,
    "content": "<html>hello world</html>"
})

test({
    "url": "http://localhost:4000/api/v1?action=next-page&hostname=http://testsite.com",
    "method": "get"
},
{
    "status": 200,
    "headers": {
        "content-type": "application/json",
        "access-control-allow-origin": "*"
    },
    "content": {
        "hostname": "http://testsite.com",
        "next-page": "/home"
    }
})

test({
    "url": "http://localhost:4000/http://testsite.com/home",
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

print 'passed: ', pass_count
print 'total: ', total
