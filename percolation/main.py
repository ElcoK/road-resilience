from os.path import dirname, join

import numpy as np
import pandas.io.sql as psql
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.plotting import figure


percolation = pd.read_csv(join('percolation','country_metrics.csv'),header=[0]) #,index_col=[0])
percolation.rename(columns={'Unnamed: 0':'country'}, inplace=True)
print(len(percolation))

# adjust some cols for better viz
percolation.Total_Edge_Length = percolation.Total_Edge_Length/1e3
percolation["color"] = "orange" 
percolation["alpha"] = 1
percolation.fillna(0, inplace=True)  # just replace missing values with zero

axis_map = {
    "Size of country": "Area",
    "Total Edge Length (in km)": "Total_Edge_Length",
    "Density": "Density",
    "Number of Edges ": "Edge_No",
    "Average Edge Length": "Ave_Path_Length",
    "Assortativity": "Assortativity",
    "Diameter": "Diameter",
    "Maximum degree": "Max_Degree",
    "log(size of country)": "areaLog",
    "log(Total Edge Length)": "edgeLog",
    "Size Country/Total Edge Length": "edgeArea",
    "log(Size Country/Total Edge Length)": "edgeAreaLog",
    "Maximum 5% Isolated" : 'max_5perc_isolated',
    "Maximum 10% Isolated" : 'max_10perc_isolated',
    "Maximum 20% Isolated" : 'max_20perc_isolated',
    "Mean 5% Isolated" : 'mean_5perc_isolated',
    "Mean 10% Isolated" : 'mean_10perc_isolated',
    "Mean 20% Isolated" : 'mean_20perc_isolated',
    "Minimum 5% Isolated" : 'min_5perc_isolated',
    "Minimum 10% Isolated" : 'min_10perc_isolated',
    "Minimum 20% Isolated" : 'min_20perc_isolated',
    "Maximum 5% Surplus Loss" : 'max_5perc_surloss_e2',
    "Maximum 10% Surplus Loss" : 'max_10perc_surloss_e2',
    "Maximum 20% Surplus Loss" : 'max_20perc_surloss_e2',
    "Mean 5% Surplus Loss" : 'mean_5perc_surloss_e2',
    "Mean 10% Surplus Loss" : 'mean_10perc_surloss_e2',
    "Mean 20% Surplus Loss" : 'mean_20perc_surloss_e2',
    "Minimum 5% Surplus Loss" : 'min_5perc_surloss_e2',
    "Minimum 10% Surplus Loss" : 'min_10perc_surloss_e2',
    "Minimum 20% Surplus Loss" : 'min_20perc_surloss_e2'        
}

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), sizing_mode="stretch_width")

# Create Input controls
gdp_cap = Slider(title="Minimum GDP per Capita (US dollar)", value=1000, start=0, end=70000, step=100)
min_net_length = Slider(title="Minimum total network length (km)", start=0, end=475000, value=0, step=1)
max_net_length = Slider(title="Maximum total network length (km)", start=0, end=475000, value=475000, step=1)
min_cntr_area = Slider(title="Minimum country size (km2)", start=0, end=10375000, value=0, step=1)
max_cntr_area = Slider(title="Maximum country size (km2)", start=0, end=10375000, value=10375000, step=1)
continent = TextInput(title="Continent:")
income_group = TextInput(title="World Bank Income Group:")
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="log(Size Country/Total Edge Length)")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="Maximum 10% Isolated")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], color=[], title=[], year=[], revenue=[], alpha=[]))

TOOLTIPS=[
    ("Country", "@title")
]

p = figure(plot_height=300, plot_width=700, title="", toolbar_location=None, tooltips=TOOLTIPS, sizing_mode="scale_both")
p.circle(x="x", y="y", source=source, size=7, color="color", line_color=None, fill_alpha="alpha")


def select_percolation():
    continent_val = continent.value.strip()
    income_group_val = income_group.value.strip()
    selected = percolation[
        (percolation.GDP_Capita >= gdp_cap.value) &
        (percolation.Total_Edge_Length >= min_net_length.value) &
        (percolation.Total_Edge_Length <= max_net_length.value) &
        (percolation.Area >= min_cntr_area.value) &
        (percolation.Area <= max_cntr_area.value) 
    ]
    if (continent_val != ""):
        selected = selected[selected.Continent.str.contains(continent_val)==True]
    if (income_group_val != ""):
        selected = selected[selected.IncomeGroup.str.contains(income_group_val)==True]
    return selected


def update():
    df = select_percolation()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d countries selected" % len(df)
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
        title=df["country"],
        alpha=df["alpha"],
    )

controls = [gdp_cap, min_net_length, max_net_length, min_cntr_area, max_cntr_area, continent, income_group, x_axis, y_axis]

for control in controls:
    control.on_change('value', lambda attr, old, new: update())

inputs = column(*controls, width=320, height=500)
inputs.sizing_mode = "fixed"
l = layout([
    [desc],
    [inputs, p],
], sizing_mode="scale_both")

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Percolation results"
