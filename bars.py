# a simple first iteration of the target app, able to handle only one user and exercise at a time.

import datetime
import natsort
from random import random
import pandas as pd
import json

from bokeh.plotting import curdoc, figure

from bokeh.layouts import column, row
from bokeh.layouts import layout
from bokeh.models import Button
from bokeh.models import Slider
from bokeh.models import Label
from bokeh.palettes import Spectral4 as COLORMAP
from bokeh.models import ColumnDataSource
from bokeh.models.ranges import Range1d


from bokeh.models.widgets.inputs import DatePicker
from bokeh.models.widgets.inputs import TextInput

from bokeh.events import ButtonClick


provisionsquellen = ['Andere ({}% v. Brutto) ', 'Eigemarkemarke ({}% v. Brutto)', 'Kombinert (E/A: {}%/{}%)', 'Neu (28% v. Netto)']
data_source = ColumnDataSource(data=dict(   provision=[],
                                            provision_neu=[],
                                            quellen=[],
                                            text=[],
                                            color=COLORMAP,
                                        ))

def set_data(umsatz=3000, anteil_hausmarke=66):
    # method for setting data based on some value
    bonus = 0.00
    if umsatz >= 1750:
        bonus = 0.03
    provision_andere = umsatz*(0.2+bonus)
    provision_eigenmarke = umsatz*(0.23+bonus)
    provision_kombiniert = (anteil_hausmarke/100) * provision_eigenmarke + (100 - anteil_hausmarke)/100 * provision_andere
    provision_neu = (umsatz / 1.19) * 0.28

    quellen = [provisionsquellen[0].format(int(100*(0.2+bonus))),
               provisionsquellen[1].format(int(100*(0.23+bonus))),
               provisionsquellen[2].format(anteil_hausmarke, 100-anteil_hausmarke),
               provisionsquellen[3]]
    provision = [provision_andere, provision_eigenmarke, provision_kombiniert, provision_neu]
    data_source.data = dict(provision=provision,
                            #provision_neu=[provision_neu],
                            quellen=quellen,
                            text=['{} €'.format(int(p)) for p in provision],
                            color=COLORMAP)
    plot.x_range.factors = quellen
    plot.y_range = Range1d(0, 1.2*max(provision))




#create plot
plot = figure( x_range=provisionsquellen,
               title='Verkaufsprovision - Altes vs neues System',
               toolbar_location=None,
               tools='',
               plot_width=800)
plot.vbar(x='quellen', top='provision', width=0.9, color='color', legend='quellen', source=data_source)
plot.text(x='quellen', y='provision', text='text', text_align='center', text_baseline='top', source=data_source)
plot.line(x=range(len(provisionsquellen)+1), y=[100]*(len(provisionsquellen)+1), line_color=COLORMAP[-1])
plot.xgrid.grid_line_color = None
plot.legend.orientation = 'horizontal'
plot.legend.location='top_center'

#set initial data
UMSATZ=2500
ANTEIL_HAUSMARKE=int(100*2/3)
set_data(UMSATZ, ANTEIL_HAUSMARKE)

#add gui elements and callbacks
anteil_slider = Slider(start=0, end=100, step=1, value=ANTEIL_HAUSMARKE, title='Anteil Eigenmarkeprodukte in %')
umsatz_slider = Slider(start=0, end=3000, step=1, value=UMSATZ, title='Umsatz pro Monat in € (Brutto)')
anteil_textinput = TextInput(value=str(ANTEIL_HAUSMARKE))
umsatz_textinput = TextInput(value=str(UMSATZ))
bonus_label = Button(label='SET ME')
provision_label = Button(label='ME TOO')

def set_label_data(umsatz, anteil):
    # set label button info. call this after setting data.
    if umsatz >= 1750:
        bonus_label.label = "Umsatz >= 1750 € : +3% Provision"
        bonus_label.button_type = 'success'
    else:
        bonus_label.label = "Umsatz < 1750 €  : Kein Bonus"
        bonus_label.button_type = 'default'


    if data_source.data['provision'][2] < data_source.data['provision'][3]:
        provision_label.label = "Neue Provision fällt geringer aus!"
        provision_label.button_type = 'warning'
    else:
        provision_label.label = "Neue Provision ist höher."
        provision_label.button_type = 'success'


set_label_data(UMSATZ, ANTEIL_HAUSMARKE)

def anteil_slider_callback(attr, old, new):
    anteil_textinput.value = str(new)
    set_data(umsatz_slider.value, new)
    set_label_data(umsatz_slider.value, new)

def umsatz_slider_callback(attr, old, new):
    umsatz_textinput.value = str(new)
    set_data(new, anteil_slider.value)
    set_label_data(new, anteil_slider.value)

def anteil_textinput_callback(attr, old, new):
    new = int(new)
    anteil_slider.value = new
    set_data(umsatz_slider.value, new)
    set_label_data(umsatz_slider.value, new)

def umsatz_textinput_callback(attr, old, new):
    new = int(new)
    umsatz_slider.value = new
    set_data(new, anteil_slider.value)
    set_label_data(new, anteil_slider.value)

anteil_slider.on_change('value', anteil_slider_callback)
umsatz_slider.on_change('value', umsatz_slider_callback)
anteil_textinput.on_change('value', anteil_textinput_callback)
umsatz_textinput.on_change('value', umsatz_textinput_callback)


layout = layout([plot,[[umsatz_slider, umsatz_textinput], [anteil_slider, anteil_textinput], [bonus_label, provision_label]]])
curdoc().add_root(layout)


if __name__ == '__main__':
    # provides an overview over all parametres
    # slow and wasteful. only do once.
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import numpy
    a = []
    u = []
    v = []
    fig = plt.figure()
    plt.title('Altes vs neues Provisionssystem. Grün = Neu gewinnt')
    plt.xlabel('Umsatz in €')
    plt.ylabel('Anteil Eigenmarke in %')


    for umsatz in range(1,3001, 5):
        for anteil in range(0,101, 1):
            set_data(umsatz, anteil)
            a.append(anteil)
            u.append(umsatz)
            v.append(data_source.data['provision'][2] < data_source.data['provision'][3])

            print(umsatz, anteil)


    plt.scatter(x=u, y=a, c=v, marker='.', linewidths=2, alpha=0.6, cmap=cm.get_cmap('RdYlGn'))
    plt.savefig('doc/überblick.pdf')
