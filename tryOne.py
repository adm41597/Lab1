from bokeh.layouts import layout
from bokeh.plotting import figure, output_file, show
from bokeh.models import Button, Slider, TextInput, AjaxDataSource, Toggle, error, Paragraph
import smtplib
import re

import numpy as np
from datetime import timedelta
from functools import update_wrapper, wraps
from six import string_types

output_file("line.html")


source = AjaxDataSource(data_url='http://localhost:5050/data',
                        polling_interval=100)


p = figure(plot_width=1200, plot_height=800, y_range=(30, 100))
#p.line('x', 'y', source=source, line_width=2)
#p.circle('x', 'y', source=source, fill_color="white", size=8)

nan=float('nan')

p.x_range.follow_interval = 10

try:
    from flask import Flask, jsonify, make_response, request, current_app
except ImportError:
    raise ImportError("You need Flask to run this example!")

def highSlider():
    slider1 = Slider(start=10, end=50, value=30, step=.5, title ="High Temp")
    return slider1

def lowSlider():
    slider2 = Slider(start=10, end=50, value=30, step=.5, title="Low Temp")
    return slider2

def text():
    text_input = TextInput(value="test", title="Phone#")
    return text_input

def lowText():
    text_input = TextInput(value="It is cold.", title="Low Temperature Message")
    return text_input

def highText():
    text_input = TextInput(value="It is hot.", title="High Temperature Message")
    return text_input

def unitToggle():
    toggle1 = Toggle(label="Units", button_type="success")
    return toggle1

def lightToggle():
    toggle2 = Toggle(label="Toggle Lights", button_type="success")
    return toggle2

def temperature():
    button1 = Button(label="Temperature"+"°C", button_type="success")
    return button1

#used to replace whats in layout if error occurs
errorMessage = " "
def errorMessage(message):
    pre = Paragraph(text=message, width=500, height=100)
    return pre


show(layout([[temperature()], [text(), highText(), lowText()], [highSlider(), lowSlider()],
             [unitToggle(), lightToggle()], p]))


def my_toggle_handler():
    #code to change light toggle with socket
    lowSlider().value= 45.0

lightToggle().on_click(my_toggle_handler)

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

hasChanged = True
currValue = 0
high = False

@app.route('/data', methods=['GET', 'OPTIONS', 'POST'])
@crossdomain(origin="*", methods=['GET', 'POST'], headers=None)
def hello_world():

    n = np.random.randint(30, 101)

    #might be backwards
    if unitToggle().active:
        n = convertToF(n)
        text().value = n + "°F"
    else:
        text().value = n + "°C"
    global hasChanged, currValue, high
    if hasChanged and n > highSlider().value:
        sendMessage(text().value, highText().value)
        currValue=n
        hasChanged = False
    elif hasChanged and n < lowSlider().value:
        sendMessage(text().value, lowText().value)
        currValue = n
        hasChanged = False

    if high and n <= currValue-5:
        hasChanged = True
    elif not high and n >= currValue+5:
        hasChanged = True
    y.append(n)
    y.pop(0)
    return jsonify(x=x[-300:], y=y[-300:])

def convertToF(temp):
    return temp*(5/9)+32

def sendMessage(num, message):
    re.sub('[0-9]', '', message)
    if not message == '':
        # smtp server for sending SMS
        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.starttls()

        server.login('logan.brownie66@gmail.com', 'Ltb122333')

        # Send text message through SMS gateway of destination number
        server.sendmail('logan.brownie66@gmail.com', num+'@email.uscc.net', message)

        server.quit()


if __name__ == "__main__":
    app.run(port=5050)
