# Eine Visualisierung der Auswirkung des zweiten von A* vorgeschlagenen Provisionssystems auf die Provisionszahlungen

"""
import natsort
from random import random
import pandas as pd
import json

from bokeh.plotting import curdoc, figure

from bokeh.layouts import column, row
from bokeh.layouts import layout
from bokeh.models import Button

from bokeh.models import Label
from bokeh.events import ButtonClick
from bokeh.models import Slider
"""

import numpy as np
from bokeh.palettes import Category20 as COLORMAP #use first four colors ofCategory20
from bokeh.models import ColumnDataSource, Band, HoverTool, Slider
from bokeh.plotting import curdoc, figure
from bokeh.layouts import layout, Spacer


# Zu visualisierende Daten kompilieren
data_source = ColumnDataSource(data={
                                    'umsatz_brutto':[],
                                    'umsatz_netto':[],
                                    'provision_alt_min':[],
                                    'provision_alt_max':[],
                                    'provision_alt_actual':[],
                                    'provisionsrate_alt':[]
                                    'provision_neu':[],
                                    'provision_neu_plusteam':[],
                                    'provisionsrate_neu':[]
                                    })

def set_data(anteil_hausmarke=0, teamumsatz=0, anteil_3prozent=0):
    # Eingabedaten generieren: Umsatzzahlen als Brutto und Nettobeträge
    umsatz_brutto = np.arange(0,5001,10)
    umsatz_netto  = umsatz_brutto/1.19

    # Generieren der (statischen) Grenzbereiche der Provisionskurven and des alten Systems.
    provisionsrate_alt = 0.20 + 0.03*(umsatz_brutto >= 1750)            # Bonus von 3% auf den Umsatz ab 1750€
    provision_alt_min  = umsatz_brutto * provisionsrate_alt             # Hier 0% Eigenmarkenanteil
    provision_alt_max  = umsatz_brutto * (provisionsrate_alt + 0.03)    # Bonus von 30% auf den Umsatz von Eigenmarken (hier 100%)
    provision_alt_actual = (1-anteil_hausmarke/100)*provision_alt_min + (anteil_hausmarke/100)*provision_alt_max

    # Generieren des (statischen) Provisionsverlaufs des neuen Systems
    provisionsrate_neu = 0.21 * (umsatz_brutto <= 500)                  # Basissatz, dann stufenweie erhöhen
    provisionsrate_neu[umsatz_brutto > 500] = 0.22                      # "bis 1500" (ab 500)
    provisionsrate_neu[umsatz_brutto > 1500] = 0.24                     # "bis 2500" (ab 1500)
    provisionsrate_neu[umsatz_brutto > 2500] = 0.26                     # "ab 2500"
    provisionsrate_neu[umsatz_brutto > 3500] = 0.28                     # "ab 3500"
    provision_neu = umsatz_netto * provisionsrate_neu
    provision_neu_plusteam = provision_neu + (1-anteil_3prozent/100)*teamumsatz*0.02 + (anteil_3prozent/100)*teamumsatz*0.03

    # register data
    data_source.data = data={
                            'umsatz_brutto':umsatz_brutto,
                            'umsatz_netto':umsatz_netto,
                            'provision_alt_min':provision_alt_min,
                            'provision_alt_max':provision_alt_max,
                            'provision_alt_actual':provision_alt_actual,
                            'provisionsrate_alt':provisionsrate_alt,
                            'provision_neu':provision_neu,
                            'provision_neu_plusteam':provision_neu_plusteam,
                            'provisionsrate_neu':provisionsrate_neu
                            }

# Visualisierung
COLORMAP = COLORMAP[4]
TOOLS = "pan,wheel_zoom,box_zoom,reset,save,box_select"
plot = figure( title='Verkaufsprovision - Altes vs neues System v2',
               tools=TOOLS,
               plot_width=1100)

# Wertebereich der alten Provision
band = Band(base='umsatz_brutto',
            lower='provision_alt_min',
            upper='provision_alt_max',
            source=data_source,
            level='underlay',
            fill_alpha=0.5,
            fill_color=COLORMAP[1],
            line_width=0,)
plot.add_layout(band)


# neue provision plus teamumsatz
band = Band(base='umsatz_brutto',
            lower='provision_neu',
            upper='provision_neu_plusteam',
            source=data_source,
            level='underlay',
            fill_alpha=0.5,
            fill_color=COLORMAP[3],
            line_width=0,)
plot.add_layout(band)



p1 = plot.line(x='umsatz_brutto', y='provision_alt_max', line_color=COLORMAP[1], line_width=3, source=data_source, legend='P-alt (untergrenze)')
p2 = plot.line(x='umsatz_brutto', y='provision_alt_min', line_color=COLORMAP[1], line_width=3, source=data_source, legend='P-alt (obergrenze)')
p3 = plot.line(x='umsatz_brutto', y='provision_alt_actual', line_color=COLORMAP[0], line_width=3, source=data_source, legend='P-alt (tatsächlich)')

# Wertebereich der neuen Provision
p4 = plot.line(x='umsatz_brutto', y='provision_neu',            line_color=COLORMAP[3], line_width=3, source=data_source, legend='P-neu (basis)')
p5 = plot.line(x='umsatz_brutto', y='provision_neu_plusteam',   line_color=COLORMAP[2], line_width=3, source=data_source, legend='P-neu (mit Teamumsatz)')


plot.xaxis.axis_label='Umsatz (Brutto)'
plot.yaxis.axis_label='Provision'
plot.legend.location='bottom_right'


# Hovertool für detailinformationen hinzufügen. TODO formatting
h = HoverTool(mode='vline')
h.tooltips = [  ('Brutto-Umsatz', '@umsatz_brutto €'),
                ('',''),
                ('P-alt: Basisrate auf Brutto',  '@provisionsrate_alt{0.00 a}'),
                ('P-alt (untergrenze)', '@provision_alt_min{0.00 a} €'),
                ('P-alt (obergrenze)', '@provision_alt_max{0.00 a} €'),
                ('P-alt (tatsächlich)', '@provision_alt_actual{0.00 a} €'),
                ('',''),
                ('P-neu: Basisrate auf Netto',  '@provisionsrate_neu{0.00 a}'),
                ('P-neu (basis)', '@provision_neu{0.00 a} €'),
                ('P-neu (mit Teamumsatz)', '@provision_neu_plusteam{0.00 a} €'),
            ]
h.renderers = [p5]
plot.add_tools(h)

# Eingabemöglichkeiten
teamumsatz=0000
anteil_hausmarke=66
anteil_3prozent=100

#UI-Steuerelemente
anteil_hausmarke_slider     = Slider(start=0, end=100,      step=1,     value=anteil_hausmarke,     title='ALT: Anteil Eigenmarkeprodukte in %')
teamumsatz_slider           = Slider(start=0, end=10000,    step=50,    value=teamumsatz,           title='NEU: Teamumsatz / Monat in € (Brutto/Netto?)')
anteil_3prozent_slider      = Slider(start=0, end=100,      step=1,     value=anteil_3prozent,      title='NEU: Anteil 3% auf Teamumsatz')
set_data(anteil_hausmarke, teamumsatz, anteil_3prozent)

#Callbacks für UI-Steuerelemente
def anteil_hausmarke_slider_callback(attr, old, new):
    global anteil_hausmarke
    anteil_hausmarke = new
    set_data(new, teamumsatz, anteil_3prozent)
anteil_hausmarke_slider.on_change('value', anteil_hausmarke_slider_callback)

def teamumsatz_slider_callback(attr, old, new):
    global teamumsatz
    teamumsatz = new
    set_data(anteil_hausmarke, new, anteil_3prozent)
teamumsatz_slider.on_change('value', teamumsatz_slider_callback)

def anteil_3prozent_slider_callback(attr, old, new):
    global anteil_3prozent
    anteil_3prozent = new
    set_data(anteil_hausmarke, teamumsatz, new)
anteil_3prozent_slider.on_change('value', anteil_3prozent_slider_callback)

layout = layout([plot, [Spacer(width_policy='max'), anteil_hausmarke_slider, Spacer(width_policy='max'), teamumsatz_slider, Spacer(width_policy='max'), anteil_3prozent_slider, Spacer(width_policy='max')]])
curdoc().add_root(layout)






