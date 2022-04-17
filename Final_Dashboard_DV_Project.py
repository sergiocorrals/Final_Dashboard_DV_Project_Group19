from asyncio.windows_events import NULL
import dash
from dash import dcc, Dash
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import dash_bootstrap_components as dbc
import base64
from bubbly.bubbly import bubbleplot
import textwrap

import warnings
warnings.filterwarnings("ignore")


# ----------------------------------------------------------------------------------------------------------------------
# Calling the app
app = Dash(external_stylesheets=[dbc.themes.GRID])


# ----------------------------------------------------------------------------------------------------------------------
# Reading the Datasets
# DF for the generic Graph
long_df = px.data.medals_long()

# Dataset Processing
#df1
df_oil_prod = pd.read_excel('bpstatsdata1.xlsx', sheet_name='Oil_Prod')

#df relative to price of oil
df_crude_oil_prices = pd.read_excel("prices.xlsx", sheet_name="Oil")

#df2
df_oil_cons_ej = pd.read_excel('Oil_Consumption_EJ.xlsx')
df_coal_cons_ej = pd.read_excel('Coal_Consumption_EJ.xlsx')
df_gas_cons_ej = pd.read_excel('Gas_Consumption_EJ.xlsx')
df_nuclear_cons_ej = pd.read_excel('Nuclear_Consumption_EJ.xlsx')
df_hydroelectricity_cons_ej = pd.read_excel('Hydroelectricity_Consumption_EJ.xlsx')
df_renewable_cons_ej = pd.read_excel('Renewable_Consumption_EJ.xlsx')
df_total_cons_ej = pd.read_excel('Total_Consumption_EJ.xlsx')

#df3
production = pd.read_excel('bpstatsdata1.xlsx', sheet_name='Oil Production - Barrels')
new_header = production.iloc[1] #grab the first row for the header
production = production[2:] #take the data less the header row
production.columns = new_header #set the header row as the df header
production = production.iloc[:,:-5]
production = production[production['Thousand barrels daily'].str.contains('Total|Other')==False]
production = production.iloc[:-14]
production = production.fillna(0)
production = production.rename(columns = {'Thousand barrels daily':'Country'})
production = production.set_index('Country')
production.columns = production.columns.astype(str)
worldmap = production.reset_index()
worldmap = production.reset_index().melt(id_vars=['Country'], var_name="Year", value_name="MBarrels/day")
worldmap_year = worldmap.groupby(['Year','Country']).sum().reset_index()
worldmap["Year"] = worldmap.Year.map(float).map(int)

#df 4
bubble = pd.read_csv("bubble.csv")

# df5
df_sectors = pd.read_excel('Consumption_by_Sector.xlsx', sheet_name="Pie2")
df_sectors2 = df_sectors.melt(id_vars=['Energy Source'], var_name="Industry", value_name="Consumption")


# ----------------------------------------------------------------------------------------------------------------------
# Dashboard Components

# Graphs
# Map Graph
fig_map = px.choropleth(worldmap,
                        locations="Country",
                        locationmode="country names",
                        color_continuous_scale="Viridis_r",
                        color="MBarrels/day",
                        hover_name="Country",
                        animation_frame="Year",
                        projection="equirectangular"
                        )

fig_map.update_layout(
    title=dict(text='Daily Oil Production',x=0.5,font=dict(family='Arial', size=18, color='#606060')),
    #title_text='World Oil Production per day',
    #title_x=0.5,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    geo=dict(
        showframe=False,
        showcoastlines=False,
    ),
    #margin=dict(t=0, b=0, l=0, r=0),
    dragmode=False)

# Bubble Graph
figure = bubbleplot(dataset=bubble, x_column='gdp_cap', y_column='RC/cap (Watt)',
                    bubble_column='Country', time_column='Year', size_column='Oil Capacity', color_column='Continent',
                    x_title="GDP per capita", y_title="Renewable Energy Capacity per capita",
                    x_logscale=False, y_logscale=False, scale_bubble=3, height=650, x_range=[0, 100000],
                    y_range=[0, 1500])

# fig_bubble = go.Figure(figure, config={'scrollzoom': True})
fig_bubble = go.Figure(figure)

fig_bubble.update_layout(
    title=dict(text='Renewable Energy Capacity, GDP per capita and Oil Capacity',
               x=0.5,font=dict(family='Arial', size=18, color='#606060')),
    #title_text="Renewable Energy Capacity and GDP per capita",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=50, l=25, r=25, b=25),
    colorway=['#800000', '#B8860B', '#778899', '#D2691E','#BC8F8F','#FFDEAD'])

fig_bubble.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightCyan')
fig_bubble.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightCyan')

# Logo Image
#logo_image = mpimg.imread('ims_logo.png')
# image_logo = dash.html.Img('ims_logo.png')
image_filename = 'ims_logo.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

# Dropdown Menus

# Dropdown Events for Graph 1 -
# dictionary containing events relative to oil prices changes
events_oil = {1862: "Start of American Civil War",
1973: "Arab countries embrace embargo towards countries supporting Israel",
1980: "Start of Iran-Iraq war",
1988: "Iraq and Iran increase output after the end of war",
2001: "9/11, invasion of Iraq, Venezuelan oil workers strike",
2008: "Global financial crisis",
2011: "Arab Spring"
}

dropdown_events = dcc.Dropdown(
    id='events_drop',
    className = "dropdown",
    options=events_oil,
    value='Start of American Civil War',
    multi=False,
    placeholder="Select an event that affected oil price change",
    clearable = False,
    style={"box-shadow" : "1px 1px 3px lightgray", "background-color" : "white"}
)

# Dropdown Countries for Graph 3 - Energy Consumption per Country and per Energy Source
dropdown_countries = dcc.Dropdown(
    id='country_drop',
    className = "dropdown",
    options=df_oil_cons_ej.columns[1:].sort_values(),
    value='Portugal',
    multi=False,
    clearable = False,
    style={"box-shadow" : "1px 1px 3px lightgray", "background-color" : "white"}
    )

# Slider Graph 4 -
slider_treemap = dcc.Slider(
    df_oil_cons_ej.Year.min(),
    df_oil_cons_ej.Year.max(),
    step=1,
    id='slider_treemap',
    className="slider",
    value=df_oil_cons_ej.Year.max(),
    marks=None, #{str(year): str(year) for year in df_oil_cons_ej.Year.unique()},
    tooltip={"placement": "bottom", "always_visible": True}
    )

# Dropdown Sources for Graph 6
sources = df_sectors2["Energy Source"].unique().tolist()
sources.remove(np.nan)

dropdown_sources = dcc.Dropdown(
    id='sources_drop',
    className = "dropdown",
    options=sources,
    value='Total',
    multi=False,
    clearable = False,
    style={"box-shadow": "1px 1px 3px lightgray", "background-color": "white"}
    )


# ----------------------------------------------------------------------------------------------------------------------
# App layout
app.layout = dbc.Container([

    # 1st Row
    dbc.Row([
        dbc.Col(html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))),width=1),
        dbc.Col([html.H1("Energy Dashboard",style={'letter-spacing': '1.5px','font-weight': 'bold','text-transform': 'uppercase'}),
                 html.H2("Data Visualization Final Project - MDAA 2022.T1", style={'margin-bottom': '5px'}),
                 html.H3("Celso Endres m20200739 | Sergio Corral 20211011 | Emanuele Aldera 20210617 | Mikala Durham m20210645",
                         style={'margin-bottom': '5px','margin-top': '5px'})],
                width=9)
    ]),

    # Intermediate Row - Story telling
    dbc.Row([
        html.P('Oil has always been a leading energy source for the global economy, but the price and availability of oil are affected '
               'considerably by political events such as war, economic factors, or pandemics, which are all nearly impossible to predict. '
               'Additionally, oil production is concentrated to areas with natural resources and economic capacity, the distribution of which '
               'has not changed much other the years. For these and other reasons, many countries have turned in the last few decades to other '
               'sources of energy, like renewables. But these sources too take economic investment, which put many countries behind. Countries '
               'like Belarus, Egypt and Iran continue to be dependent on oil and gas, while European countries like Portugal and Germany are able'
               ' to invest in a diverse energy portfolio. Europe appears to be leading the pack in terms of renewable energy capacity as well. ',
               id="storytelling1", style={"font-style": "italic",'font-size':'18px', 'padding': '10px 10px 2px'}),
        html.P('Finally, we can see that residential energy use, which gets much of the attention in terms of behavioural adjustments and energy '
               'reduction strategies, is a small fraction (15%) of global energy usage. Whether increasing renewable energy production or reduction'
               ' of dependency on oil is a goal moving forward, industry and transportation sectors have to be on board or the results will be negligible. '
               'This dashboard provides evidence of the above findings, as well as other opportunities to explore global energy patterns.',
               id="storytelling3", style={"font-style": "italic",'font-size':'18px', 'padding': '0px 10px 10px'})
    ]),

    # Intermediate Row - DropDown Menu
    dbc.Row(dbc.Col(html.Div(dropdown_events),width=6, style={'padding': '0px 15px 0px'})),

    # 2nd Row
    dbc.Row([
        dbc.Col(html.Div(
            dcc.Graph(id="lineplot", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white"})),
            width=6,
            style={'padding':'2px 15px 15px 15px'}),
        dbc.Col(html.Div(
            dcc.Graph(id="map", figure=fig_map, style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white"})),
            width=6,
            style={'padding':'2px 15px 15px 15px'})
    ]),

    # Intermediate Row - DropDown Menu
    dbc.Row([dbc.Col(html.Div(dropdown_countries),
                     width=6,
                     style={'padding': '0px 15px 0px'}),
             dbc.Col(html.Div(),
                     width=6)]),

    # 3rd Row
    dbc.Row([

        # 1st Column - Graph 3 - Energy Consumption per Country and per Energy Source
        dbc.Col(html.Div(
            dcc.Graph(id="barplot", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white", 'height':'505px'})),
            width=6,
            style={'padding':'2px 15px 15px 15px'}),

        # 2nd Column - Graph 4 -
        dbc.Col(html.Div([
            dcc.Graph(id="treeplot", style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white"}),
            html.Div(['Select Year',slider_treemap],
                     style={'text-align':'center',
                            'font-weight':'bold',
                            'box-shadow':'1px 1px 3px lightgray',
                            "background-color" : "white"})]),
            width=6,
            style={'padding':'0px 15px 15px 15px'})]),

    # Intermediate Row - DropDown Menu
    dbc.Row([dbc.Col(html.Div(), width=8, style={'padding': '0px 15px 0px'}),
             dbc.Col(html.Div(dropdown_sources), width=4, style={'padding': '0px 15px 0px'})]),

    # 4th Row
    dbc.Row([
        dbc.Col(html.Div(
            dcc.Graph(id='bubble',figure=fig_bubble,
                      style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white"})),
            width=8,
            style={'padding':'2px 15px 15px 15px'}),
        dbc.Col(html.Div(
            dcc.Graph(id="piechart",
                      style={'box-shadow':'1px 1px 3px lightgray', "background-color" : "white", 'height':'650px'} )),
            width=4,
            style={'padding':'2px 15px 15px 15px'})])],

    #Container
    fluid=True,
    style={'background-color':'#F2F2F2',
           'font-family': 'sans-serif',
           'color': '#606060',
           'font-size':'14px'
           })


# ----------------------------------------------------------------------------------------------------------------------
# Callbacks
@app.callback(
    [Output(component_id='lineplot', component_property='figure'),
     Output(component_id='piechart', component_property='figure')],
    [Input('events_drop', 'value'),
     Input('sources_drop', 'value')])

############################################First line Plot##########################################################
def plot(event, source):
    # data_1 = dict(type='scatter', x=df_oil_prod.columns.to_list()[1:], y=df_oil_prod.iloc[5, 1:])
    data_11 = dict(type='scatter', x=df_crude_oil_prices["Year"], y=df_crude_oil_prices["$ 2020"],
                   name='Cost per barrel (considering inflation)', marker_color="#962f0f")
    data_12 = dict(type='scatter', x=df_crude_oil_prices["Year"], y=df_crude_oil_prices["$ money of the day"],
                   name="Cost per barrel (in today's dollars)", marker_color="#004172")

    data_1 = [data_11, data_12]

    layout_1 = dict(title=dict(
        text='Oil Price',x=0.5, font=dict(family='Arial', size=18, color='#606060')
    ),
        xaxis=dict(title='Year'),
        yaxis=dict(title='US dollars'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
        ,
        legend=dict(
            orientation="v",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=50, l=25, r=25, b=25)
    )

    fig_price = go.Figure(data=data_1, layout=layout_1)

    fig_price.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightCyan')
    fig_price.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightCyan')

    if event != 0:
        fig_price.add_vline(x=event, line_width=1.5, line_dash="dash", line_color="black")


    ##################################### Pie CHART ########################

    selected_values = df_sectors2["Consumption"][df_sectors2["Energy Source"] == source]
    labels = df_sectors2["Industry"][df_sectors2["Energy Source"] == source]

    fig_pie = px.pie(df_sectors2,
                     values=selected_values,
                     names=labels,
                     color_discrete_sequence=["#962f0f", "#004172", "#3d9970", "#e2898e", "#ff7f1f"])

    fig_pie.update_layout(
        title=dict(text='Global Energy Consumption by Industry Sector (2018)',x=0.5, font=dict(family='Arial', size=18, color='#606060')),
        #title_text="Consumption by source - What is it used for",
        #title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, l=25, r=25, b=25))

    return fig_price, fig_pie

@app.callback(
    [Output(component_id='barplot', component_property='figure'),
     Output(component_id='treeplot', component_property='figure')],
    [Input('country_drop', 'value'),
     Input('slider_treemap', 'value')])

def plots(country, year_treemap):
    ############################################Stacked bar Plot######################################################

    data_3 = [
        go.Bar(name='Oil', x=df_oil_cons_ej['Year'], y=df_oil_cons_ej[country].round(2), marker_color="#962f0f"),
        go.Bar(name='Coal', x=df_coal_cons_ej['Year'], y=df_coal_cons_ej[country].round(2), marker_color="#813772"),
        go.Bar(name='Gas', x=df_gas_cons_ej['Year'], y=df_gas_cons_ej[country].round(2), marker_color="#6f7200"),
        go.Bar(name='Nuclear', x=df_nuclear_cons_ej['Year'], y=df_nuclear_cons_ej[country].round(2),
               marker_color="#7f0052"),
        go.Bar(name='Hydroelectricity', x=df_hydroelectricity_cons_ej['Year'],
               y=df_hydroelectricity_cons_ej[country].round(2), marker_color="#004172"),
        go.Bar(name='Renewable', x=df_renewable_cons_ej['Year'], y=df_renewable_cons_ej[country].round(2),
               marker_color="#3d9970"),
        go.Scatter(name='Total', x=df_total_cons_ej['Year'], y=df_total_cons_ej[country].round(2), line_color='#000000')
    ]

    layout_3 = dict(title=dict(text='Energy Consumption by Source - ' + country,
                               x=0.5,
                               font=dict(family='Arial', size=18, color='#606060')),
                    xaxis=dict(linecolor='rgb(204, 204, 204)', ticks='outside', nticks=15, tickangle=-45),
                    yaxis=dict(title='Consumption in Exajoules', linecolor='rgb(204, 204, 204)', ticks='outside'),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    barmode='stack',
                    margin=dict(t=50, l=25, r=25, b=25)
                    )

    fig_stackedbars = go.Figure(data=data_3, layout=layout_3)

    fig_stackedbars.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightCyan')
    fig_stackedbars.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightCyan')

    ############################################Treemap Plot######################################################

    values_4 = [0,
                float(df_oil_cons_ej[df_oil_cons_ej["Year"] == year_treemap][country].round(2)),  # oil
                float(df_gas_cons_ej[df_gas_cons_ej["Year"] == year_treemap][country].round(2)),  # gas
                float(df_coal_cons_ej[df_coal_cons_ej["Year"] == year_treemap][country].round(2)),  # coal
                float(df_nuclear_cons_ej[df_nuclear_cons_ej["Year"] == year_treemap][country].round(2)),  # nuclear
                float(
                    df_hydroelectricity_cons_ej[df_hydroelectricity_cons_ej["Year"] == year_treemap][country].round(2)),
                # Hydroelectric
                float(
                    df_renewable_cons_ej[df_renewable_cons_ej["Year"] == year_treemap][country].round(2))]  # Renewable

    labels_4 = [country, "Oil", "Gas", "Coal", "Nuclear", "Hydroelectricity", "Renewable"]
    parents_4 = ["", country, country, country, country, country, country]
    colors = ["rgba(0,0,0,0)", "#962f0f", "#6f7200", "#813772", "#7f0052", "#004172", "#3d9970"]
    hovers_4 = [float(df_total_cons_ej[df_total_cons_ej["Year"] == year_treemap][country].round(2)),
                float(df_oil_cons_ej[df_oil_cons_ej["Year"] == year_treemap][country].round(2)),  # oil
                float(df_gas_cons_ej[df_gas_cons_ej["Year"] == year_treemap][country].round(2)),  # gas
                float(df_coal_cons_ej[df_coal_cons_ej["Year"] == year_treemap][country].round(2)),  # coal
                float(df_nuclear_cons_ej[df_nuclear_cons_ej["Year"] == year_treemap][country].round(2)),  # nuclear
                float(
                    df_hydroelectricity_cons_ej[df_hydroelectricity_cons_ej["Year"] == year_treemap][country].round(2)),
                # Hydroelectric
                float(df_renewable_cons_ej[df_renewable_cons_ej["Year"] == year_treemap][country].round(2))]

    fig_treemap = go.Figure(
        go.Treemap(labels=labels_4, values=values_4, parents=parents_4, hoverinfo="text", hovertext=hovers_4,
                   root_color="rgba(0,0,0,0)", marker_colors=colors))

    fig_treemap.update_layout(
        title=dict(text='Country Zoom-in - Energy Consumption by Source (EJ)',x=0.5,font=dict(family='Arial', size=18, color='#606060')),
        #title_text="Consumption per Source of Energy",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, l=25, r=25, b=25)
    )

    return fig_stackedbars, fig_treemap


# ----------------------------------------------------------------------------------------------------------------------
# Running the app
if __name__ == '__main__':
    app.run_server(debug=True)