from cs50 import SQL
from dash import html, dcc, Input, Output, State, dash_table
from holidays import country_holidays
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, datetime

from app import *

tab_card = {'height': '100%'}

config_graph={'displayModeBar': True, 
              'showTips': True, 
              'displaylogo': False}

db = SQL('sqlite:///project.db')

holidays = country_holidays('BR', subdiv='MG')

# ========== Import Database ========== #

def updateDataFrame():

    query = db.execute("SELECT clients.name client, projects.name project, task_id, tasks.name task, demand, people_id, people.name person, teams.name team, start_date, end_date, tasks.due_date due_date, hours_day, total_hours FROM TaskAssign, Tasks, People, Projects, Teams, Clients WHERE task_id = tasks.id AND people_id = people.id AND tasks.project_id = projects.id AND people.team_id = teams.id AND projects.client_id = clients.id")
    return pd.DataFrame(query)
    
df =  updateDataFrame()

layout = dbc.Container(children=[

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([ 
                        html.H5(' Astra Planner', className='p-2 bi bi-bar-chart-steps')
                    ]),
                    dbc.Stack([
                        dbc.Label('Selecione o Período:'),
                        dcc.DatePickerRange(id='update-dates',
                            min_date_allowed=date(2020, 1, 1),
                            max_date_allowed=date(2030, 12, 31),
                            start_date=df.start_date.min(),
                            end_date=df.end_date.max(),
                            initial_visible_month=datetime.today(),
                            className='DatePicker'),

                        dbc.Button('Atualizar', color='light', id='update-dashboard')
                    ], gap=2)
                ])
            ], style=tab_card)
        ], sm=12, lg=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Stack([
                        dcc.Graph(id='graph1', className='dbc', config=config_graph)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=10),
    ], style={'margin-top': '20px'}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Stack([
                        dcc.Graph(id='graph2', className='dbc', config=config_graph)
                    ]),
                ])
            ], style=tab_card)
        ], sm=12, lg=12),
    ], style={'margin-top': '20px'}),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Stack([
                        dcc.Graph(id='graph3', className='dbc', config=config_graph)
                    ])
                ])
            ], style=tab_card)
        ], sm=12, lg=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Stack([
                        dcc.Graph(id='graph4', className='dbc', config=config_graph)
                    ]),
                ])
            ], style=tab_card)
        ], sm=12, lg=4),
    ], style={'margin-top': '20px'}),
    
# Timelines
    
    html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Stack([
                            dcc.Graph(id='graph5', className='dbc', config=config_graph)
                        ]),
                    ])
                ], style=tab_card)
            ], sm=12, lg=12),
        ], style={'margin-top': '20px'}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Stack([
                            dcc.Graph(id='graph6', className='dbc', config=config_graph)
                        ]),
                    ])
                ], style=tab_card)
            ], sm=12, lg=12),
        ], style={'margin-top': '20px'}),
    ], id='timelines'),
    dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5('Resumo de Tarefas'),
                        html.Br(),
                        dbc.Container([
                            dash_table.DataTable( 
                                style_header={
                                    'backgroundColor': 'rgb(0, 0, 0)',
                                    'font-family':'Lato',
                                    'color': 'white',
                                    'font-size':'14px',
                                    'font-weight':'700'
                                },
                                style_data={
                                    'backgroundColor': 'rgb(17, 17, 17)',
                                    'font-family':'Lato',
                                    'color': 'white',
                                    'font-size':'12px',
                                }, id='tbl')
                        ], id='report'),
                        html.Br(),
                    ])
                ], style=tab_card)
            ], sm=12, lg=12),
        ], id='reports', style={'margin-top': '20px'}),
    


], fluid=True, style={'height': '100vh'})

# =========  Callbacks  =========== #

@app.callback(
    [Output('graph1', 'figure'), Output('graph2', 'figure'),
     Output('graph3', 'figure'), Output('graph4', 'figure')],
    [Input('update-dashboard', 'n_clicks')],
    [State('update-dates', 'start_date'), State('update-dates', 'end_date')]
)
def gengraphs(n, start, end):
    
# Create hour demand and hour capacity dataframes   
    df =  updateDataFrame()

    subset = df.loc[:,['client', 'project', 'task', 'demand', 'due_date', 'total_hours']].groupby(['client', 'project', 'task']).agg({'demand': 'first', 'total_hours':'sum'}).reset_index()

    query = db.execute("SELECT clients.name client, projects.name project, tasks.name task, demand, tasks.due_date FROM Tasks, Projects, Clients WHERE tasks.project_id = projects.id AND projects.client_id = clients.id")
    tasks = pd.DataFrame(query)

    subset = pd.merge(subset, tasks, how='outer').fillna(0).sort_values(by=['client', 'project']).sort_values(by=['client','project']).reset_index()
    
    dates = pd.bdate_range(start, end, holidays=holidays[start:end], freq='C')
    
    demand = pd.DataFrame(
    columns = df.person.unique(),
    index = dates).fillna(0)

    demand = demand.rename_axis("person", axis="columns")

    capacity = pd.DataFrame(
        columns = df.person.unique(),
        index = dates).fillna(8)

    capacity = capacity.rename_axis('person', axis='columns')

    for index, row in df.iterrows():
        demand.loc[row['start_date']:row['end_date'], row.person] += row.hours_day
        
    demand['Assigned'] = 0
    demand['Assigned'] = demand.sum(axis=1)
        
    people = pd.DataFrame(db.execute('SELECT teams.name team, people.name FROM people, teams WHERE team_id = teams.id'))


    capacity['Total'] = 0
    capacity['Total'] = capacity.sum(axis=1)

# Create Indicators
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode = 'number',
        value = capacity.loc[start:end, 'Total'].count(),
        title= {'text': 'Dias Úteis'},
        domain = {'row': 0, 'column': 0},
    ))


    fig.add_trace(go.Indicator(
        mode = 'number',
        value = demand.loc[start:end, 'Assigned'].sum(),
        title= {'text': 'Horas Atribuídas'},
        domain = {'row': 0, 'column': 1},
        #delta = {'reference': 400, 'relative': True, 'position' : 'top'}
    ))

    fig.add_trace(go.Indicator(
        mode = 'number',
        value = subset.loc[subset['total_hours'] == 0, 'demand'].sum(),
        title= {'text': 'Horas a Atribuir'},
        #delta = {'reference': demand.loc[start:end, 'Assigned'].sum() + df.loc[df['total_hours'] == 0, 'demand'].sum()},
        domain = {'row': 0, 'column': 2},
    ))

    fig.add_trace(go.Indicator(
        mode = 'number+delta',
        value = capacity.loc[start:end, 'Total'].sum(),
        title= {'text': 'Capacidade'},
        delta = {'reference': demand.loc[start:end, 'Assigned'].sum() + subset.loc[subset['total_hours'] == 0, 'demand'].sum()},
        domain = {'row': 0, 'column': 3},
    ))


    fig.update_layout(
        grid = {'rows': 1, 'columns': 4, 'pattern': 'independent',},
        template='plotly_dark',
        height=350
    )
    
# Create Global demand x capacity graph
    
    fig1 = px.bar(
        demand['Assigned'], 
        barmode='overlay', 
        color_discrete_sequence=px.colors.qualitative.Dark24, 
        opacity=1,
        labels={
            'index': '',
            'value': 'Horas',
            'variable':'',
            'Assigned':'Horas Atribuídas',
            'Capacity':'Capacidade'
        },
        title='Horas Atribuídas x Capacidade',
    )
    
    fig1.add_trace(go.Bar(x=capacity.index , y=capacity['Total'], opacity=0.1, name='Capacity'))
    
    fig1.update_layout(
        template='plotly_dark',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )
    
    demand = demand.drop('Assigned', axis=1)

# Create teams graphs as facets
    
    fig2 = px.bar(demand, facet_col='person', facet_col_wrap=2,
             labels={
                     'index': '',
                     'value': '',
                     'person': 'Pessoa'
                 },
            title='Horas Atribuídas / Pessoa',
            height=800,
            color_discrete_sequence=px.colors.qualitative.Alphabet)
    
    fig2.update_layout(
        template='plotly_dark',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )
    
    fig2.for_each_xaxis(lambda x: x.update(showgrid=False, showticklabels=True))
    fig2.for_each_yaxis(lambda x: x.update(showgrid=False))
    fig2.for_each_annotation(lambda a: a.update(text=''))

# Create Teams indicators
    
    fig3 = go.Figure()

    n = 0

    for person in df.person.unique():
        fig3.add_trace(go.Indicator(
            mode = 'number+gauge', value = demand[person].sum(),
            title = {'text' : person, 'font_size' : 14},
            domain = {'row': n, 'x': [0.25, 1]},
            gauge = {
                'shape': 'bullet',
                'axis': {'range': [None, capacity[person].sum()]},
                'steps': [
                    {'range': [0, demand[person].sum()], 'color': '#2E91E5'},
                    {'range': [demand[person].sum(), capacity[person].sum()], 'color': 'rgba(58, 45, 43, 25)'}],
                'bar': {'color': '#2E91E5'}}))
        n += 1

    fig3.update_layout(
        grid = {'rows': n+1, 'columns': 1, 'pattern': 'independent', 'ygap': 0.6},
        template='plotly_dark',
        height= 600)
    
    return [fig, fig1, fig2, fig3]

# Create timelines


@app.callback(
    [Output('graph5', 'figure'), Output('graph6', 'figure'),],
    [Input('update-dashboard', 'n_clicks')],
)
def gentimelines(n):
 
    df =  updateDataFrame()
    df['end_date'] = pd.to_datetime(df['end_date'])
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = df['end_date'] + pd.to_timedelta(23.99, unit='h')
    
    fig5 = px.timeline(df, 
                       x_start='start_date', 
                       x_end='end_date', y='task', 
                       color='project', 
                       labels={
                         'task': '',
                         'project': 'Projeto'}, 
                       title='Cronograma de Projetos',)
    
    fig5.update_yaxes(autorange='reversed')
    
    fig5.update_layout(
        height=700,
        template='plotly_dark',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5))
    
    fig6 = px.timeline(df, 
                       x_start='start_date', 
                       x_end='end_date', 
                       y='person', 
                       color='person',
                       labels={'person': ''},
                       title='Cronograma Individual',)
    
    fig6.update_yaxes(autorange='reversed') 
    
    fig6.update_layout(
        template='plotly_dark',
        legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.4,
                xanchor="center",
                x=0.5))
    
    return[fig5, fig6]


@app.callback(
    Output('tbl', 'data'),
    [Input('update-dashboard', 'n_clicks')],
)
def gentable(n):
    
    df =  updateDataFrame()
 
    report1 = df.loc[:,['client', 'project', 'task', 'demand', 'due_date', 'total_hours']].groupby(['client', 'project', 'task']).agg({'demand': 'first', 'total_hours':'sum'}).reset_index()

    query = db.execute("SELECT clients.name client, projects.name project, tasks.name task, demand, tasks.due_date FROM Tasks, Projects, Clients WHERE tasks.project_id = projects.id AND projects.client_id = clients.id")
    tasks = pd.DataFrame(query)

    report1 = pd.merge(report1, tasks, how='outer').fillna(0).sort_values(by=['client', 'project']).sort_values(by=['client','project'])

    report1['% Alocado'] = report1['total_hours']/report1['demand']*100

    report1 = report1.rename(columns={'client':'Cliente','project':'Projeto','task':'Tarefa','demand':'Demanda', 'total_hours':'Alocada(Horas)', 'due_date':'Prazo'}, errors='raise')
    
    return report1.to_dict('records')


