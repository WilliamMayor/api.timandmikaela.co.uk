import urllib
import os

from functools import wraps

import requests

from flask import (Flask, request, render_template, redirect, jsonify)

app = Flask(__name__)
app.debug = True

def redirectable(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            results = f(*args, **kwargs)
            if 'redirect' in request.form:
                params = urllib.urlencode(results)
                return redirect(
                    '%s?%s' % (request.form['redirect'], params),
                    code=303)
            else:
                return jsonify(results=results)
        except AssertionError as ae:
            if 'redirect_error' in request.form:
                params = urllib.urlencode({'error': ae.args[0]})
                return redirect(
                    '%s?%s' % (request.form['redirect_error'], params),
                    code=303)
            else:
                return jsonify(error=ae.args[0]), 400
        except Exception as e:
            if 'redirect_error' in request.form:
                params = urllib.urlencode({'error': str(e)})
                return redirect(
                    '%s?%s' % (request.form['redirect_error'], params),
                    code=303)
            raise e
    return decorated_function

@app.after_request
def access_control(response):
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response

@app.route('/rsvp/', methods=["POST"])
@redirectable
def rsvp():
    f = request.form
    assert f.get('name', '') != '', 'Missing name'
    assert f.get('response', '') in ['accept', 'decline'], 'Unknown response'
    body = render_template(
        'rsvp.html',
        name=f.get('name'),
        response=f.get('response'))
    send_email(
        ['tim@timandmikaela.co.uk', 'mikaela@timandmikaela.co.uk'],
        'You got an RSVP!',
        body)
    return {'message': 'RSVP Sent!'}


def send_email(to, subject, body, _from='Tim and Mikaela <admin@timandmikaela.co.uk>'):
    r = requests.post(
        "https://api.mailgun.net/v2/timandmikaela.co.uk/messages",
        auth=("api", os.environ['MAILGUN_API_KEY']),
        data={"from": _from,
              "to": to,
              'cc': 'admin@timandmikaela.co.uk',
              "subject": subject,
              "text": body})
    if r.status_code != 200:
        raise Exception('Could not send email: %s' % r.text)
