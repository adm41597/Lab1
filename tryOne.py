from bokeh.layouts import layout
from bokeh.plotting import figure, output_file, show
from bokeh.models import Button, Slider, TextInput, WidgetBox, AjaxDataSource, Toggle, error, PreText
from bokeh.models import Paragraph
from bokeh.models.callbacks import CustomJS
from bokeh import events
from bokeh.io import curdoc
import smtplib

import numpy as np
from datetime import timedelta
from functools import update_wrapper, wraps
from six import string_types
from pymsgbox import *

import socket
import sys

HOST = '192.168.1.88'
PORT = 80
output_file("line.html")


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


#def lightscallback(value):
#    if value == True:
#        value = False
#    else:
#        value = True
#    return value


def temperature():
    button1 = Button(label="Temperature"+"°C", button_type="success")
    return button1


# used to replace whats in layout if error occurs
def errorMessage(errText):
    pre = PreText(text="""Your text is initialized with the 'text' argument.

    The remaining Paragraph arguments are 'width' and 'height'. For this example,
    those values are 500 and 100 respectively.""",
                  width=500, height=100)
    pre = Paragraph(text=errText, width=500, height=100)
    return pre


def convertToF(temp):
    return temp*(5/9)+32


def sendMessage(num, message):
    # smtp server for sending SMS
    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()

    server.login('logan.brownie66@gmail.com', 'Ltb122333')

    # Send text message through SMS gateway of destination number
    server.sendmail('logan.brownie66@gmail.com', num+'@email.uscc.net', message)

    server.quit()

connect = True

while connect:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        err ="Error creating socket 1: "+str(e)
        print(err)
        randomvar = alert(text="No data available", title="Error", button="OK")
        continue


    try:
        s.connect((HOST, PORT))
    except socket.error as e:
        err = "Connection error 2: "+str(e)+"\n(Box and/or ethernet is probably off.)"
        print(err)
        randomvar = alert(text="No data available", title="Error", button="OK")
        #s.close()
        continue

    try:
        s.sendall(b'p')
    except socket.error as e:
        err = "Error sending data 3: "+str(e)
        print(err)
        randomvar = alert(text="No data available", title="Error", button="OK")
        #s.close()
        continue

    try:
        data = s.recv(1024)
    except socket.error as e:
        err = "Error receiving data 4: "+str(e)
        print(err)
        randomvar = alert(text="No data available", title="Error", button="OK")
        #s.close()
        continue
    connect = False
    break

nan = float('nan')
m = []
check2 = True
#lightsOn = False

source = AjaxDataSource(data_url='http://localhost:5050/data',
                        polling_interval=1000)
tools = ["hover", "pan", "wheel_zoom", "reset"]

p = figure(plot_width=1200, plot_height=800, y_range=(10, 50), tools=tools,
           x_axis_label="Seconds Ago from current time", y_axis_label="Temp, °C", y_axis_location="right")

p.multi_line(xs='x', ys='y', source=source, line_width=2)

p.x_range.start = -305
p.x_range.end = 0
p.x_range.follow_interval = 10

try:
    from flask import Flask, jsonify, make_response, request, current_app
except ImportError:
    raise ImportError("You need Flask to run this example!")

#lights = Button(label="Toggle Lights", button_style="success")
#lightsOn = lights.js_on_event(events.ButtonClick, lightscallback(lightsOn))

show(layout([[temperature()], [text(), highText(), lowText()], [highSlider(), lowSlider()], [unitToggle(),
     lightToggle()], p]))

#lights.on_click(change_click())

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

x = list(range(-300, 1))
y = [0 for xx in x]
m = list(range(0, 301))
m.reverse()

@app.route('/data', methods=['GET', 'OPTIONS', 'POST'])
@crossdomain(origin="*", methods=['GET', 'POST'], headers=None)
def hello_world():
    global m
    global check2
    global s
    #global lightsOn
    check = True
    check3 = True
    #n = np.random.randint(30, 101)

    if check2:
        #while check3:
        try:
            #if lightsOn == True:
                #s.sendall(b'pt')
                #lightsOn = False
            #else:
            s.sendall(b'p')
        except ConnectionResetError as e:
            err = "Error sending data 5: " + str(e)+"\n(Box turned off or ethernet unplugged.)"
            print(err)
            #alert(text="No data available", title="Error", button="OK")
            check = False
            check2 = False
            check3 = False
            #s.close()
            #break
        except socket.error as e:
            err = "Error sending data 6: " + str(e)
            print(err)
            #randomvar2 = alert(text="No data available", title="Error", button="OK")
            check = False
            check2 = False
            check3 = False
            #s.close()
            #break

        try:
            santa = s.recv(1024)
        except socket.error as e:
            err = "Error receiving data 7: " + str(e)
            print(err)
            #randomvar2 = alert(text="No data available", title="Error", button="OK")
            check = False
            check2 = False
            check3 = False
            #s.close()
            #break
        #break
    else:
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except socket.error as e:
                err = "Error creating socket 8: " + str(e)
                print(err)
                #randomvar2 = alert(text="No data available", title="Error", button="OK")
                check = False
                break

            try:
                s.connect((HOST, PORT))
            except socket.error as e:
                err = "Connection error 9: " + str(e) + "\n(Box and/or ethernet is probably off.)"
                print(err)
                #randomvar2 = alert(text="No data available", title="Error", button="OK")
                check = False
                s.close()
                break

            try:
                s.sendall(b'p')
            except socket.error as e:
                err = "Error sending data 10: " + str(e)
                print(err)
                #randomvar2 = alert(text="No data available", title="Error", button="OK")
                check = False
                #s.close()
                break

            try:
                data = s.recv(1024)
            except socket.error as e:
                err = "Error receiving data 11: " + str(e)
                print(err)
                #randomvar2 = alert(text="No data available", title="Error", button="OK")
                check = False
                #s.close()
                break

            try:
                s.sendall(b'p')
            except ConnectionResetError as e:
                err = "Error sending data 12: " + str(e) + "\n(Box turned off or ethernet unplugged.)"
                print(err)
                #randomvar2 = alert(text="No data available", title="Error", button="OK")
                check = False
                #s.close()
                break
            except socket.error as e:
                err = "Error sending data 13: " + str(e)
                print(err)
                #randomvar2 = alert(text="No data available", title="Error", button="OK")
                check = False
                #s.close()
                break

            try:
                santa = s.recv(1024)
            except socket.error as e:
                err = "Error receiving data 14: " + str(e)
                print(err)
                #randomvar2 = alert(text="No data available", title="Error", button="OK")
                check = False
                #s.close()
                break
            check2 = True
            break

    if check:
        n = repr(santa)
        f = n.split("'")
        h = f[1]
        #y.append(n)
        #y.pop(0)
        #if h == 'e':
            #randomvar3 = alert(text="Wire is unplugged from box.", title="Error", button="OK")
        print("Value is "+str(n))
        print(str(len(m)))
    else:
        h = 'e'

    if h == 'e':
        m.append(1)
        h = -300
    print(str(len(m)))

    y.append(h)
    y.pop(0)

    newx = x[-300:]
    newy = y[-300:]

    newx2 = []
    newy2 = []

    if len(m) == 0:
        newx2.append(newx[-300:])
        newy2.append(newy[-300:])

    if len(m) != 0:
        i = 0
        while i < len(m):
            #print("i="+str(i)+", m="+str(m[i]))
        #if m[i] == 1:
        #    newx = newx[-300:-m[i]-1]
        #    newy = newy[-300:-m[i]-1]
        #elif m[i] == 300:
        #    newx = newx[-m[i]+1:]
        #    newy = newy[-m[i]+1:]
        #else:
        #    newx = newx[-300:-m[i]-1]+newx[-m[i]+1:]
        #    newy = newy[-300:-m[i]-1]+newy[-m[i]+1:]
            #logic before this is good
            if len(m) == 1:
                if m[i] == 1:
                    newx2.append(newx[-300:-m[i]])
                    newy2.append(newy[-300:-m[i]])
                elif m[i] == 300:
                    newx2.append(newx[-m[i]+1:])
                    newy2.append(newy[-m[i]+1:])
                else:
                    newx2.append(newx[-300:-m[i]])
                    newx2.append(newx[-m[i]+1:])
                    newy2.append(newy[-300:-m[i]])
                    newy2.append(newy[-m[i]+1:])
            elif i == len(m)-1:
                if m[i] == 1 and m[i-1]+2 != m[i]:
                    newx2.append(newx[-m[i-1]+2:-m[i]])
                    newy2.append(newy[-m[i-1]+2:-m[i]])
                elif m[i-1]+2 != m[i]:
                    newx2.append(newx[-m[i-1]+2:-m[i]])
                    newy2.append(newy[-m[i-1]+2:-m[i]])
                    newx2.append(newx[-m[i]+1:])
                    newy2.append(newy[-m[i]+1:])
                else:
                    newx2.append(newx[-m[i]+1:])
                    newy2.append(newy[-m[i]+1:])
                    # logic to here I think is good
            else:
                if i == 0 and m[i] != 300:
                    newx2.append(newx[:-m[i]])
                    newy2.append(newy[:-m[i]])
                elif m[i] != 300 and m[i-1] != m[i] and m[i-1]+2 != m[i]:
                    newx2.append(newx[-m[i-1]+2:-m[i]])
                    newy2.append(newy[-m[i-1]+2:-m[i]])
                # logic after here is good
            m[i] += 1
            if m[i] == 301:
                del m[i]
            i += 1
    #v = 300 - len(m)
    #return jsonify(x=newx[-v:], y=newy[-v:])
    print(str(newx2) + ",/n" + str(newy2))
    v = len(newx2)
    return jsonify(x=newx2[:v], y=newy2[:v])


if __name__ == "__main__":
    app.run(port=5050)