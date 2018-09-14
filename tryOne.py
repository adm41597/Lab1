from bokeh.layouts import layout
from bokeh.plotting import figure, output_file, show
from bokeh.models import Button, Slider, TextInput, WidgetBox, AjaxDataSource
import smtplib

import numpy as np
from datetime import timedelta
from functools import update_wrapper, wraps
from six import string_types

output_file("line.html")
# *** WORKS ***
server = smtplib.SMTP("smtp.gmail.com", 587)

server.starttls()

###server.login('logan.brownie66@gmail.com', 'Ltb122333')

# Send text message through SMS gateway of destination number

###server.sendmail('logan.brownie66@gmail.com', '3195308365@email.uscc.net', 'Salutations')

server.quit()

source = AjaxDataSource(data_url='http://localhost:5050/data',
                        polling_interval=100)
p = figure(plot_width=1200, plot_height=800, y_range=(30, 100))
p.line('x', 'y', source=source, line_width=2)
p.circle('x', 'y', source=source, fill_color="white", size=8)

nan=float('nan')

p.x_range.follow_interval = 10

try:
    from flask import Flask, jsonify, make_response, request, current_app
except ImportError:
    raise ImportError("You need Flask to run this example!")

def slider():
    slider1 = Slider(start=-15, end=60, value=0, step=.1, title ="High Temp")
    slider2 = Slider(start=-15, end=60, value=0, step=.1, title ="Low Temp")
    widgets = WidgetBox(slider1, slider2)
    return widgets


def text():
    text_input = TextInput(value="test", title="Phone#")
    return text_input


def button():
    button1 = Button(label="Units", button_type="success")
    return button1


show(layout([[text(), button()], [slider()], p]))

#########################################################
# Flask server related
#
# Taken from Bokeh ajax_source.py example.
#########################################################


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    #"""
    #Decorator to set crossdomain configuration on a Flask view
    #For more details about it refer to:
    #http://flask.pocoo.org/snippets/56/
    #"""
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))

    if headers is not None and not isinstance(headers, string_types):
        headers = ', '.join(x.upper() for x in headers)

    if not isinstance(origin, string_types):
        origin = ', '.join(origin)

    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            requested_headers = request.headers.get(
                'Access-Control-Request-Headers'
            )
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            elif requested_headers:
                h['Access-Control-Allow-Headers'] = requested_headers
            return resp
        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


app = Flask(__name__)

x = list(range(0, 300))
y = [0 for xx in x]

@app.route('/data', methods=['GET', 'OPTIONS', 'POST'])
@crossdomain(origin="*", methods=['GET', 'POST'], headers=None)
def hello_world():
    n = np.random.randint(30, 101)
    y.append(n)
    y.pop(0)
    return jsonify(x=x[-300:], y=y[-300:])


if __name__ == "__main__":
    app.run(port=5050)