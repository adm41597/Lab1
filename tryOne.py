from bokeh.plotting import figure, output_file, show
import random

output_file("line.html")

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
show(p)

#print(y_axis)
#print(n)

