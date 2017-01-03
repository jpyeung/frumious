# this is a test script for qhex functions and flask.
# the standard usage is thus:
# 1) run this code.
# 2) while code is running, go to localhost:5000/q?tool=caesarshift&p=apple
# you should see the standard output of the caesarshift code in your browser.

from flask import Flask, request
from caesarshiftPY import caesarshift


app = Flask(__name__)

@app.after_request
def treat_as_plain_text(response):
    response.headers["content-type"] = "text/plain"
    return response

@app.route("/q")
def query():
    tool = request.args.get('tool')
    payload = request.args.get('p')
    if tool == 'caesarshift':
        return caesarshift(payload)
    else:
        return('%s not implemented' % tool)


if __name__ == "__main__":
    app.run()