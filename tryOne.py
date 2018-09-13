from bokeh.layouts import layout
from bokeh.plotting import figure, output_file, show
from bokeh.models import Button, Slider, TextInput, WidgetBox
import random
import smtplib

output_file("line.html")
# *** WORKS ***
server = smtplib.SMTP("smtp.gmail.com", 587)

server.starttls()

###server.login('logan.brownie66@gmail.com', 'Ltb122333')

# Send text message through SMS gateway of destination number

###server.sendmail('logan.brownie66@gmail.com', '3195308365@email.uscc.net', 'Salutations')

server.quit()


def plot():
    p = figure(plot_width=1200, plot_height=800, x_range=(0,300), y_range=(30,100))

    x_axis = list(range(0,301))

    y_axis=[]
    nan=float('nan')

    i=0
    while i<301:
        y_axis.append(nan)
        i+=1

#print("got to here")
#p.line(x_axis, y_axis, line_width=2)
#p.circle(x_axis, y_axis, fill_color="white", size=8)
#show(p)

    i=0
    while i<301:
        n=random.randint(30,100)
        y_axis.append(n)
        y_axis.pop(0)
        i+=1
#    p.line(x_axis, y_axis, line_width=2)
#    p.circle(x_axis, y_axis, fill_color="white", size=8)
#    p.update()
#print("got to here")

    p.line(x_axis, y_axis, line_width=2)
    p.circle(x_axis, y_axis, fill_color="white", size=8)
    #show(p)
    return p


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


show(layout([[text(), button()], [slider()], [plot()]]))

#print(y_axis)
#print(n)

