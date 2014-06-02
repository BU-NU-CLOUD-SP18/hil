"""This is the HaaS API server - it provides the HaaS's rest api.

This module only marshalls between HTTP and the routines in haas.api; it doesn't
directly ipmlement the semantics of the API.

To start the server, or the module can be run as a script, e.g. (from the root
of the source tree):

    python haas/api_server.py

Right now the server is always run in debug mode, which isn't safe for
production use. When we get close to release-quality we'll have to change this.
"""

from flask import Flask, request
from haas import config, model, api


def api_function(f):
    """A decorator which adds some error handling.

    If the function decorated with `api_function` raises an exception of type
    `api.APIError`, the error will be reported to the client, whereas other
    exceptions (being indications of a bug in the HaaS) will not be.
    """
    def wrapped(*args, **kwargs):
        try:
            resp = f(*args, **kwargs)
        except api.APIError as e:
            # Right now we're always returning 400 (Bad Request). This probably
            # isn't actually the right thing to do.
            #
            # Additionally, we're getting deprecation errors about the use of
            # the message attribute. TODO: figure out what the right way to do
            # this is.
            return e.message, 400
        if not resp:
            return ''
    return wrapped



app = Flask(__name__)


@app.route('/user/<username>', methods=['PUT', 'DELETE'])
@api_function
def user(username):
    """Handle create/delete user commands."""
    if request.method == 'PUT':
        return api.user_create(username, request.form['password'])
    else: # DELETE
        return api.user_delete(username)


if __name__ == '__main__':
    config.load()
    model.init_db(create=True)
    app.run(debug=True)
