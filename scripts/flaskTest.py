# this is a test script for qhex functions and flask.
# the standard usage is thus:
# 1) run this code.
# 2) while code is running, go to localhost:5000/q?tool=caesarshift&p=apple
# you should see the standard output of the caesarshift code in your browser.

from flask import Flask, request, make_response
from caesarshiftPY import caesarshift


app = Flask(__name__)
#app = Flask(__name__, static_url_path='')

#@app.after_request
#def treat_as_plain_text(response):
#    response.headers["content-type"] = "text/plain"
#    return response

@app.route('/')
def root():
    #resp = make_response()
    #resp.headers["content-type"] = "text/html"
    return app.send_static_file('index.html')

@app.route("/q", methods=['GET', 'POST'])
def query():
    tool = request.args.get('tool')
    if request.method == 'POST': #have not tested yet....
        payload = request.form
    else:
        payload = request.args.get('p')
        
    if tool == 'caesarshift':
        resp = make_response(caesarshift(payload))
        resp.headers["content-type"] = "text/plain"
        return resp
    else:
        return('%s not implemented' % tool)


if __name__ == "__main__":
    app.run()