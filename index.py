from dash import Input, Output, html, dcc, State
from holidays import country_holidays
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from cs50 import SQL
from dash.exceptions import PreventUpdate
import time
from datetime import date, datetime

from app import *
from components import dashboard


db = SQL('sqlite:///project.db', 1)

holidays = country_holidays('BR', subdiv='MG')

# ========== Global functions to update dropdown items ========== #

# Define functions to update dropdown lists

def update_teams():

    rows = db.execute('SELECT name FROM teams')
    return [html.Option(value=item['name']) for item in rows]

def update_people():

    rows = db.execute('SELECT name FROM people')
    return [html.Option(value=item['name']) for item in rows]

def update_clients():

    rows = db.execute('SELECT name FROM clients')
    return [html.Option(value=item['name']) for item in rows]

def update_projects():

    rows = db.execute('SELECT name FROM projects')
    return [html.Option(value=item['name']) for item in rows]

def update_tasks(project):
    
    rows = db.execute('SELECT name FROM tasks WHERE project_id = ?', project)
    return [html.Option(value=item['name']) for item in rows]
    

# Define SQL search functions

def search_team(name):
    return db.execute('SELECT * FROM teams WHERE name = ?', name)

def search_people(name):
    return db.execute('SELECT people.id, people.name, email, teams.name team, phone FROM people, teams WHERE people.name = ? AND team_id = teams.id', name)

def search_client(name):
    return db.execute('SELECT * FROM clients WHERE name = ?', name)

def search_project(name):
    return db.execute('SELECT projects.id, projects.name, clients.name client, due_date, done FROM projects, clients WHERE client_id = clients.id AND projects.name = ?', name)

def search_task(name, project_id):
    return db.execute('SELECT * FROM tasks WHERE name = ? AND project_id = ?', name, project_id)

def search_assign(task_id, people_id):
    return db.execute('SELECT * FROM TaskAssign WHERE task_id = ? AND people_id = ?', task_id, people_id)


# ==========  Page Layout  ========== #


app.layout = dbc.Container([
# ==========  NavBar Layout  ========== #
    dcc.Location(id='url'),
    
    # SideNav
    dbc.Col([
        dbc.Col([
            dbc.Row(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink('Dashboard', active='exact', class_name='p-2 li-head')),
                    dbc.NavItem(dbc.NavLink(' Overview', href='/', active='exact', class_name='li bi bi-clipboard-data-fill')),
                    dbc.NavItem(dbc.NavLink(' Timelines', href='#timelines', active='exact', class_name='li bi bi-calendar-range-fill', external_link=True)),
                    dbc.NavItem(dbc.NavLink(' Reports', href='#reports', active='exact', class_name='li bi bi-graph-up-arrow', external_link=True))
                ], vertical=True, navbar=True), class_name='p-3'),
            dbc.Row(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink('Database', active='exact', class_name='p-2 li-head')),
                    dbc.NavItem(dbc.NavLink(' People', href='#', id='btn-people-xl', n_clicks=0, class_name='li bi bi-person-fill')),
                    dbc.NavItem(dbc.NavLink(' Teams', href='#', id='btn-teams-xl', n_clicks=0, class_name='li bi bi-people-fill')),
                    dbc.NavItem(dbc.NavLink(' Clients', href='#', id='btn-clients-xl', n_clicks=0, class_name='li bi bi-building-fill')),
                    dbc.NavItem(dbc.NavLink(' Projects', href='#', id='btn-projects-xl', n_clicks=0, class_name='li bi bi-kanban-fill')),
                    dbc.NavItem(dbc.NavLink(' Tasks', href='#', id='btn-tasks-xl', n_clicks=0, class_name='li bi bi-list-check'))
                ], vertical=True, navbar=True), class_name='p-3')
        ], class_name='d-none d-xl-block'),
        dbc.Col([
            dbc.Row(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink(active='exact', class_name='li-head bi bi-house-fill')),
                    dbc.NavItem(dbc.NavLink(href='/', active='exact', class_name='li bi bi-clipboard-data-fill')),
                    dbc.NavItem(dbc.NavLink(href='#timelines', active='exact', class_name='li bi bi-calendar-range-fill', external_link=True)),
                    dbc.NavItem(dbc.NavLink(href='#reports', active='exact', class_name='li bi bi-graph-up-arrow', external_link=True))
                ], vertical=True, navbar=True)),
            dbc.Row(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink(active='exact', class_name='li-head bi bi-database-fill')),
                    dbc.NavItem(dbc.NavLink(href='#', id='btn-people-sm', n_clicks=0, class_name='li bi bi-person-fill')),
                    dbc.NavItem(dbc.NavLink(href='#', id='btn-teams-sm', n_clicks=0, class_name='li bi bi-people-fill')),
                    dbc.NavItem(dbc.NavLink(href='#', id='btn-clients-sm', n_clicks=0, class_name='li bi bi-building-fill')),
                    dbc.NavItem(dbc.NavLink(href='#', id='btn-projects-sm', n_clicks=0, class_name='li bi bi-kanban-fill')),
                    dbc.NavItem(dbc.NavLink(href='#', id='btn-tasks-sm', n_clicks=0, class_name='li bi bi-list-check'))
                ], vertical=True, navbar=True))
        ], class_name='d-block d-xl-none')
    ], lg=2, sm=1, className='sideMenu'),
    # Content
    dbc.Col([
        html.Div(id='page-content'),
    ], lg=10, sm=11, className='content'),

# ==========  Modal Layouts  ========== #
    
    # People Modal
    
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('People')),
        dbc.ModalBody([
            dbc.Row([
                dbc.Stack([
                    dbc.Input(type='number', id='people-id', placeholder='ID', readonly=True, class_name='IdInput'),
                    dbc.Input(type='text', placeholder='Person Name', list='people', id='people-name'),
                    dbc.Input(type='email', placeholder='Email', id='people-email')
                ], direction='horizontal', gap=2)
            ]),
            html.Br(), 
            dbc.Row([    
                dbc.Stack([
                    dbc.Input(type='text', placeholder='Team', list='teams', id='people-team'),
                    dbc.Input(type='text', placeholder='Phone', id='people-phone'),
                    dbc.Button('Add/Update', color='info', id='add-people', class_name='ms-auto'),
                    dbc.Button('Remove', color='dark', id='rm-people')    
                ], direction='horizontal', gap=2),
            ]),
            html.Br(), 
            dbc.Alert(id='add-people-alert', color='info', is_open=False,duration=2000),
            dbc.Alert(id='rm-people-alert', color='info', is_open=False,duration=2000),
            dbc.ModalFooter(dbc.Switch(label='Lock ID', value=False, id='people-lockid')),
        ]),
    ],  id='modal-people', size='lg', fullscreen='xl-down',is_open=False),
    
    # Clients Modal
    
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Clients')),
        dbc.ModalBody([
            dbc.Row([
                dbc.Stack([
                    dbc.Input(type='number', placeholder='ID', id='client-id', readonly=True, class_name='IdInput'),
                    dbc.Input(type='text', placeholder='Client Name', list='clients', id='client-name'),
                    dbc.Input(type='email', placeholder='Email', id='client-email')
                ], direction='horizontal', gap=2)
            ]),
        html.Br(), 
            dbc.Row([
                dbc.Stack([
                    dbc.Button('Add/Update', color='info', id='add-client', class_name='ms-auto'),
                    dbc.Button('Remove', color='dark', id='rm-client')    
                ], direction='horizontal', gap=2),
            ]),
            html.Br(),
            dbc.Alert(id='add-clients-alert', color='info', is_open=False,duration=2000),
            dbc.Alert(id='rm-clients-alert', color='info', is_open=False,duration=2000),
            dbc.ModalFooter(dbc.Switch(label='Lock ID', value=False, id='clients-lockid')),
        ]),
    ],  id='modal-clients', size='lg', fullscreen='xl-down', is_open=False),
    
    # Teams Modal
    
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Teams')),
        dbc.ModalBody([
           dbc.Row([
               dbc.Stack([
                   dbc.Input(type='number', placeholder='ID', id='team-id', readonly=True, class_name='IdInput'),
                   dbc.Input(type='text', placeholder='Team Name', list='teams', id='team-name'),
                ], direction='horizontal', gap=2)
            ]),
            html.Br(), 
            dbc.Row([
                dbc.Stack([
                    dbc.Button('Add/Update', color='info', id='add-team', class_name='ms-auto'),
                    dbc.Button('Remove', color='dark', id='rm-team')    
                ], direction='horizontal', gap=2),
            ]),
            html.Br(),
            dbc.Alert(id='add-teams-alert', color='info', is_open=False, duration=2000),
            dbc.Alert(id='rm-teams-alert', color='info', is_open=False, duration=2000),
            dbc.ModalFooter(dbc.Switch(label='Lock ID', value=False, id='teams-lockid')),
        ]),
    ],  id='modal-teams', size='lg', fullscreen='xl-down', is_open=False),
    
    # Projects Modal
    
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Projects')),
        dbc.ModalBody([
            dbc.Row([
                dbc.Stack([
                    dbc.Input(type='number', placeholder='ID', id='project-id', readonly=True, class_name='IdInput'),
                    dbc.Input(type='text', placeholder='Project Name', list='projects', id='project-name'),
                ], direction='horizontal', gap=2)
            ]),
            html.Br(), 
            dbc.Row([
                dbc.Stack([
                    dbc.Input(type='text', placeholder='Client Name', list='clients', id='project-client'),
                    dbc.Label('Due Date:', class_name='mx-2 text-nowrap'),
                    dcc.DatePickerSingle(id='project-date',
                        min_date_allowed=date(2020, 1, 1),
                        max_date_allowed=date(2030, 12, 31),
                        date=None,
                        initial_visible_month=datetime.today(),
                        className='DatePicker'),
                ], direction='horizontal', gap=2), 
            ]),
            html.Br(), 
            dbc.Row([
                dbc.Stack([
                    dbc.Switch(label='Completed', value=False, id='check-project'),
                    dbc.Button('Add/Update', color='info', id='add-project', class_name='ms-auto'),
                    dbc.Button('Remove', color='dark', id='rm-project')    
                ], direction='horizontal', gap=2),
            ]),
            html.Br(),
            dbc.Alert(id='add-projects-alert', color='info', is_open=False,duration=2000),
            dbc.Alert(id='rm-projects-alert', color='info', is_open=False,duration=2000),
            dbc.ModalFooter([
                dbc.Switch(label='Lock ID', value=False, id='projects-lockid')
            ]),
        ]),
    ],  id='modal-projects', size='lg', fullscreen='xl-down',is_open=False),
    
    # Tasks Modal
    
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Tasks')),
        dbc.ModalBody([
            dbc.Label('Edit Task', size='lg'),
            html.Br(),
            dbc.Row([
                dbc.Label('Project'),
                dbc.Stack([
                    dbc.Input(type='number', placeholder='ID', id='task-project-id', readonly=True, class_name='IdInput'),
                    dbc.Input(type='text', list='projects', placeholder='Select a Project', id='task-project'),
                ], direction='horizontal', gap=2),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Stack([
                    dbc.Input(type='number', placeholder='ID', id='task-id', readonly=True, class_name='IdInput'),
                    dbc.Input(type='text', list='tasks', placeholder='Task Name', id='task-name'),
                    dbc.Label('Due Date:', class_name='mx-2 text-nowrap'),
                    dcc.DatePickerSingle(id='task-date',
                        min_date_allowed=date(2020, 1, 1),
                        max_date_allowed=date(2030, 12, 31),
                        date=None,
                        initial_visible_month=datetime.today(),
                        className='DatePicker'),
                ], direction='horizontal', gap=2),
            ]),
            html.Br(), 
            dbc.Row([
                dbc.Stack([
                    dbc.Col([
                        dbc.Label('Est. Demand (Hours):'),
                        dbc.Input(type='number', id='task-demand', class_name='NumberInput'),
                    ]),
                    dbc.Col([
                        dbc.Label('Hours Assigned:'),
                        dbc.Input(type='number', id='hours-assigned', class_name='NumberInput', readonly=True),
                    ]),
                    dbc.Col([
                        dbc.Label('Assigned to:'),
                        dcc.Dropdown(
                            id='dropdown-assign',
                            disabled=True,
                            multi=True,
                        ),
                    ], width=6),
                ], direction='horizontal', gap=2),     
            ]),
            html.Br(),
            dbc.Row([
                dbc.Stack([
                    dbc.Switch(label='Completed', value=False, id='check-task', class_name='mx-2 ms-auto'),
                    dbc.Button('Add/Update', color='info', id='add-task'),
                    dbc.Button('Remove', color='dark', id='rm-task'),
                ], direction='horizontal', gap=2),     
            ]),
            html.Br(),
            dbc.Label('Assign Task', size='lg'),
            html.Br(),
            dbc.Row([
                dbc.Label('Assign to'),
                dbc.Stack([
                    dbc.Input(type='number', placeholder='ID', id='task-people-id', readonly=True, class_name='IdInput'),
                    dbc.Input(type='text', list='people', placeholder='People',id='task-people'),
                ], direction='horizontal', gap=2),     
            ]),
            html.Br(),
            dbc.Row([
                dbc.Label('Assignment Interval'),
                dbc.Stack([
                    dcc.DatePickerRange(id='task-assign-dates',
                        min_date_allowed=date(2020, 1, 1),
                        max_date_allowed=date(2030, 12, 31),
                        start_date=None,
                        end_date=None,
                        initial_visible_month=datetime.today(),
                        minimum_nights=0,
                        className='DatePicker'),
                    dbc.Label('Hours/Day:', class_name='mx-2 text-nowrap ms-auto'),
                    dbc.Input(type='number', id='assignment-hours', class_name='NumberInput'),
                    dbc.Label('Total Hours:', class_name='mx-2 text-nowrap'),
                    dbc.Input(type='number', id='total-hours', class_name='NumberInput', readonly=True),
                ], direction='horizontal', gap=2),     
            ]),
            html.Br(),
            dbc.Row([
                dbc.Stack([
                    dbc.Button('Assign/Update', color='info', id='assign-task', class_name='ms-auto'),
                    dbc.Button('Unassign', color='secondary', id='unassign-task'),
                ], direction='horizontal', gap=2),     
            ]),
            html.Br(),
            dbc.Alert(id='add-tasks-alert', color='info', is_open=False,duration=2000),
            dbc.Alert(id='rm-tasks-alert', color='info', is_open=False,duration=2000),
            dbc.Alert(id='assign-tasks-alert', color='info', is_open=False,duration=2000),
            dbc.Alert(id='unassign-tasks-alert', color='info', is_open=False,duration=2000),
            dbc.ModalFooter([
                dbc.Switch(label='Lock ID', value=False, id='tasks-lockid')
            ]),
        ]),
    ],  id='modal-tasks', size='lg', fullscreen='xl-down',is_open=False),

    
    html.Datalist(id='teams', children=update_teams()),
    html.Datalist(id='people', children=update_people()),
    html.Datalist(id='clients', children=update_clients()),
    html.Datalist(id='projects', children=update_projects()),
    html.Datalist(id='tasks'),

], fluid=True)


# ==========  Render page Callback  ========== #

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def render_template(pathname):
    if pathname == '/':
        return dashboard.layout
    

# ==========   Teams Modal Callbacks  ========== #

# Update Fields

@app.callback(
    Output('team-id', 'value'),
    [Input('team-name', 'value'), Input('teams-lockid', 'value')],
)
def updatefields_teams(name, lock):
    
    if lock:
        raise PreventUpdate
    
    else:
        result = search_team(name)
        
        if len(result) == 0:
            return None
        
        else:
            return result[0]['id']
# Update Database
        
@app.callback(
    [Output('add-teams-alert', 'children'), Output('add-teams-alert', 'is_open'), 
     Output('add-teams-alert', 'color')], 
    [Input('add-team', 'n_clicks')], 
    [State('add-teams-alert', 'is_open'), State('team-name','value'),
    State('team-id', 'value')]
)
def editteam(n, is_open, name, id):

    if n is None:
        raise PreventUpdate

    elif name is None:
        message = 'Please provide a valid team name.'
        color='dark'
        
    elif id is None:
        db.execute('INSERT INTO teams (name) VALUES (?)', name)
        message = name + ' Added.'
        color='info'
    
    else:
        db.execute('UPDATE teams SET name = ? WHERE id = ?', name, id)
        message = name + ' Updated.'
        color='info'

    return [message, not is_open, color]

# Remove from Database

@app.callback(
    [Output('rm-teams-alert', 'children'), Output('rm-teams-alert', 'is_open'), 
     Output('rm-teams-alert', 'color')], 
    [Input('rm-team', 'n_clicks')], 
    [State('rm-teams-alert', 'is_open'), State('team-name','value'),
    State('team-id','value')]
)
def rmteam(n, is_open, name, id):

    if n is None:
        raise PreventUpdate

    elif None in [name, id]:
        message = 'Please select a valid team name.'
        color='dark'
        
    elif len(db.execute('SELECT * FROM people WHERE team_id = ?', id)) != 0:
        message = 'Team already linked to one or more people.'
        color='dark'
        
    else:
        db.execute('DELETE FROM teams WHERE id = ?', id)
        message = name + ' Removed.'
        color='info'

    return [message, not is_open, color]

# ==========   Clients Modal Callbacks  ========== #

# Update Fields

@app.callback(
    [Output('client-email', 'value'), Output('client-id', 'value')],
    [Input('client-name', 'value'), Input('clients-lockid', 'value')],
)
def updatefields_clients(name, lock):
    
    if lock:
        raise PreventUpdate
    
    else:
        result = search_client(name)
        
        if len(result) == 0:
            return [None, None]
        
        else:
            return [result[0]['email'], result[0]['id']]
 
@app.callback(
    [Output('add-clients-alert', 'children'), Output('add-clients-alert', 'is_open'), 
     Output('add-clients-alert', 'color')], 
    [Input('add-client', 'n_clicks')], 
    [State('add-clients-alert', 'is_open'), State('client-name','value'), 
     State('client-email','value'), State('client-id', 'value')]
)
def updateclient(n, is_open, name, email, id):

    if n is None:
        raise PreventUpdate

    elif None in [name]:
        message = 'Please provide all requested information.'
        color='dark'
        
    elif id is None:
        db.execute('INSERT INTO clients (name, email) VALUES (?, ?)', name, email)
        message = name + ' Added.'
        color='info'
        
    else:
        db.execute('UPDATE clients SET name = ?, email = ? WHERE id = ?', name, email, id)
        message = name + ' Updated.'
        color='info'

    return [message, not is_open, color]

# Remove from Database

@app.callback(
    [Output('rm-clients-alert', 'children'), Output('rm-clients-alert', 'is_open'), 
     Output('rm-clients-alert', 'color')], 
    [Input('rm-client', 'n_clicks')], 
    [State('rm-clients-alert', 'is_open'), State('client-name', 'value'),
    State('client-id', 'value')]
)
def rmclient(n, is_open, name, id):

    if n is None:
        raise PreventUpdate

    elif id is None:
        message = 'Please select a valid client name.'
        color='dark'
    
    elif len(db.execute('SELECT * FROM projects WHERE client_id = ?', id)) != 0:
        message = 'Client already linked to one or more projects.'
        color='dark'
        
    else:
        db.execute('DELETE FROM clients WHERE id = ?', id)
        message = name +' Removed.'
        color='info'

    return [message, not is_open, color]

# ==========   People Modal Callbacks  ========== #

# Update Fields

@app.callback(
    [Output('people-id', 'value'), Output('people-email', 'value'), Output('people-team', 'value'), 
     Output('people-phone', 'value')],
    [Input('people-name', 'value'), Input('people-lockid', 'value')],
)
def updatefields_people(name, lock):
    
    if lock:
        raise PreventUpdate
    
    else:
        result = search_people(name)
        
        if len(result) == 0:
            return [None, None, None, None]
        
        else:
            result = result[0]
            return [result['id'], result['email'], result['team'], result['phone']]
    
# Update Datebase
    
@app.callback(
    [Output('add-people-alert', 'children'), Output('add-people-alert', 'is_open'), 
     Output('add-people-alert', 'color')], 
    [Input('add-people', 'n_clicks')], 
    [State('add-people-alert', 'is_open'), State('people-name','value'), 
     State('people-email','value'), State('people-team','value'), 
     State('people-phone','value'), State('people-id', 'value')]
)
def editpeople(n, is_open, name, email, team, phone, id):
    
    team_id = search_team(team)

    if n is None:
        raise PreventUpdate

    elif None in [name, email, team, phone]:
        message = 'Please provide all information requested.'
        color='dark'
        
    elif len(team_id) == 0:
        message = 'Team does not exist.'
        color='dark'
        
    elif id is None:
        db.execute('INSERT INTO people (name, email, team_id, phone) VALUES (?, ?, ?, ?)', name, email, team_id[0]['id'], phone)
        message = name + ' Added.'
        color='info'
    
    else:
        db.execute('UPDATE people SET name = ?, email = ?, team_id = ?, phone = ? WHERE id = ?', name, email, team_id[0]['id'], phone, id)
        message = name + ' Updated.'
        color='info'

    return [message, not is_open, color]

# Remove from Database

@app.callback(
        [Output('rm-people-alert', 'children'), Output('rm-people-alert', 'is_open'), 
         Output('rm-people-alert', 'color')], 
        [Input('rm-people', 'n_clicks')], 
        [State('rm-people-alert', 'is_open'), State('people-name','value'),
         State('people-id', 'value')]
)
def rmpeople(n, is_open, name, id):

    if n is None:
        raise PreventUpdate

    elif id is None:
        message = 'Please select a valid name.'
        color='dark'
             
    elif len(db.execute('SELECT * FROM taskassign WHERE people_id = ?', id)) != 0:
        message = 'Person already linked to one or more tasks.'
        color='dark'
    
    else:
        db.execute('DELETE FROM people WHERE id = ?', id)
        message = name + ' Removed.'
        color='info'

    return [message, not is_open, color]

# ==========   Projects Modal Callbacks  ========== #

@app.callback(
    [Output('project-id', 'value'), Output('project-client', 'value'), 
     Output('project-date', 'date'), Output('check-project', 'value')],
    [Input('project-name', 'value'), Input('projects-lockid', 'value')],
)
def updatefields_project(name, lock):
    
    if lock:
        raise PreventUpdate
    
    else:
        result = search_project(name)
        
        if len(result) == 0:
            return [None, None, None, False]
        
        else:
            result = result[0]
            return [result['id'], result['client'], result['due_date'], result['done']]

# Update Database - Projects

@app.callback(
    [Output('add-projects-alert', 'children'), Output('add-projects-alert', 'is_open'),
     Output('add-projects-alert', 'color')], 
    [Input('add-project', 'n_clicks')], 
    [State('add-projects-alert', 'is_open'), State('project-name','value'), 
     State('project-client','value'), State('project-date', 'date'), 
     State('check-project', 'value'), State('project-id', 'value')]
)
def editproject(n, is_open, name, client, date, done, id):

    if n is None:
        raise PreventUpdate

    elif None in [name, client, date]:
        message = 'Please provide all information requested.'
        color='dark'
        
    elif len(search_client(client)) == 0:
        message = 'Client not found.'
        color='dark'
        
    else:
        client_id = search_client(client)[0]['id']
        
        if id is None:
            db.execute('INSERT INTO projects (name, client_id, due_date, done) VALUES (?, ?, ?, ?)', name, client_id, date, done)
            message = name + ' Added.'
            color='info'
        
        else:
            db.execute('UPDATE projects SET name = ?, client_id = ?, due_date = ?, done = ? WHERE id =  ?', name, client_id, date, done, id)
            message = name +' Updated.'
            color='info'

    return [message, not is_open, color]

# Remove from Database

@app.callback(
        [Output('rm-projects-alert', 'children'), Output('rm-projects-alert', 'is_open'), 
         Output('rm-projects-alert', 'color')], 
        [Input('rm-project', 'n_clicks')], 
        [State('rm-projects-alert', 'is_open'), State('project-name','value'),
        State('project-id', 'value')]
)
def rmproject(n, is_open, name, id):

    if n is None:
        raise PreventUpdate

    elif id is None:
        message = 'Must Select a Project'
        color='dark'
             
    elif len(db.execute('SELECT * FROM tasks WHERE project_id = ?', id)) != 0:
        message = 'Project already linked to one or more tasks'
        color='dark'
        
    else:
        db.execute('DELETE FROM projects WHERE id = ?', id)
        message = name + ' Removed.'
        color='info'

    return [message, not is_open, color]

# ==========   Tasks Modal Callbacks  ========== #

@app.callback(
    [Output('task-id', 'value'), Output('task-demand', 'value'), 
     Output('task-date', 'date'), Output('check-task', 'value'),
     Output('hours-assigned', 'value'), Output('dropdown-assign', 'value'),
     Output('dropdown-assign', 'options')],
    [Input('task-name', 'value'), Input('tasks-lockid', 'value'),
     Input('rm-task', 'n_clicks'), Input('assign-task', 'n_clicks'), 
     Input('unassign-task', 'n_clicks')],
    [State('task-project-id', 'value')]
)
def updatefields_tasks(name, lock, n1, n2, n3, project):
    
    if lock:
        raise PreventUpdate
    
    else:
        result = search_task(name, project)
        
        if len(result) == 0:
            return [None, None, None, False, None, [], []]
        
        else:
            result = result[0]
            hours = db.execute('SELECT SUM(total_hours) hours FROM TaskAssign WHERE task_id = ?', result['id'])[0]['hours']
            people = [person['name'] for person in db.execute('SELECT people.name name FROM TaskAssign, People WHERE people.id = people_id AND task_id = ?', result['id'])]
            return [result['id'], result['demand'], result['due_date'], result['done'], hours, people, people]
        
# Update Database - Tasks

@app.callback(
    [Output('add-tasks-alert', 'children'), Output('add-tasks-alert', 'is_open'),
     Output('add-tasks-alert', 'color')], 
    [Input('add-task', 'n_clicks')], 
    [State('add-tasks-alert', 'is_open'), State('task-name','value'), 
     State('task-demand','value'), State('task-date', 'date'), 
     State('check-task', 'value'), State('task-project-id', 'value'),
     State('task-id', 'value')]
)
def editproject(n, is_open, name, demand, date, done, project, id):

    if n is None:
        raise PreventUpdate

    elif None in [name, demand, date, project]:
        message = 'Please provide all information requested.'
        color='dark'
        
    elif id is None:
        db.execute('INSERT INTO tasks (name, project_id, due_date, demand, done) VALUES (?, ?, ?, ?, ?)', name, project, date, demand, done)
        message = name + ' Added.'
        color='info'
        
    else:
        db.execute('UPDATE tasks SET name = ?, project_id = ?, due_date = ?, demand = ?, done = ? WHERE id =  ?', name, project, date, demand, done, id)
        message = name + ' Updated.'
        color='info'

    return [message, not is_open, color]

# Remove from Database

@app.callback(
        [Output('rm-tasks-alert', 'children'), Output('rm-tasks-alert', 'is_open'), 
         Output('rm-tasks-alert', 'color')], 
        [Input('rm-task', 'n_clicks')], 
        [State('rm-tasks-alert', 'is_open'), State('task-name','value'),
        State('task-id', 'value')]
)
def rmproject(n, is_open, name, id):

    if n is None:
        raise PreventUpdate

    elif id is None:
        message = 'Must Select a Task'
        color='dark'
    
    elif len(db.execute('SELECT * FROM taskassign WHERE task_id = ?', id)) != 0:
        message = 'Task already assigned.'
        color='dark'
        
    else:
        db.execute('DELETE FROM tasks WHERE id = ?', id)
        message = name+ ' Removed.'
        color='info'

    return [message, not is_open, color]

# Calculate total Hours

@app.callback(
    Output('total-hours', 'value'),
    [Input('assignment-hours', 'value'), Input('task-assign-dates', 'start_date'), 
     Input('task-assign-dates', 'end_date')]
)
def updatefields_project(hours, start, end):
    
    if None in [start, end, hours]:
        return None
    
    else:
        return len(pd.bdate_range(start, end, holidays=holidays[start:end], freq='C')) * hours
       
# Assign tasks to people        

        
@app.callback(
    [Output('assign-tasks-alert', 'children'), Output('assign-tasks-alert', 'is_open'), 
     Output('assign-tasks-alert', 'color')], 
    [Input('assign-task', 'n_clicks')], 
    [State('assign-tasks-alert', 'is_open'), State('task-id', 'value'),
     State('task-assign-dates', 'start_date'), State('task-assign-dates', 'end_date'),
     State('assignment-hours', 'value'), State('total-hours', 'value'),
     State('task-people-id', 'value')]
)
def assign_task(n, is_open, id, start, end, hours, total, people_id):

    if n is None:
        raise PreventUpdate

    elif None in [id, start, end, hours, total, people_id]:
        message = 'Please provide all requested information.'
        color='dark'
        
    else:
        result = search_assign(id, people_id)
        
        if len(result) == 0:
            
            db.execute('INSERT INTO TaskAssign (task_id, people_id, start_date, end_date, hours_day, total_hours) VALUES (?, ?, ?, ?, ?, ?)', 
                       id, people_id, start, end, hours, total)
            message = 'Task Assigned.'
            color='info'

        else:
            db.execute('UPDATE TaskAssign SET start_date = ?, end_date = ?, hours_day = ?, total_hours = ? WHERE task_id = ? AND people_id = ?', 
                       start, end, hours, total, id, people_id)
            message = 'Assignment Updated.'
            color='info'

    return [message, not is_open, color]

# Unassign tasks  

@app.callback(
    [Output('unassign-tasks-alert', 'children'), Output('unassign-tasks-alert', 'is_open'), 
     Output('unassign-tasks-alert', 'color')], 
    [Input('unassign-task', 'n_clicks')], 
    [State('unassign-tasks-alert', 'is_open'), State('task-id', 'value'),
     State('task-people-id', 'value')]
)
def unassign_task(n, is_open, id, people_id):

    if n is None:
        raise PreventUpdate

    elif None in [id, people_id]:
        message = 'Please provide all requested information.'
        color='dark'
        
    else:
        result = search_assign(id, people_id)
        
        if len(result) == 0:
            
            message = 'Task not assigned for this person.'
            color='dark'

        else:
            db.execute('DELETE FROM TaskAssign WHERE task_id = ? AND people_id = ?', id, people_id)
            message = 'Task Unassigned.'
            color='info'

    return [message, not is_open, color]
        


# ==========   Toggle Modal Callbacks  ========== #

def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

app.callback(
    Output('modal-people', 'is_open'), 
    [Input('btn-people-xl', 'n_clicks'), Input('btn-people-sm', 'n_clicks')], 
    [State('modal-people', 'is_open')],
)(toggle_modal)

app.callback(
    Output('modal-teams', 'is_open'), 
    [Input('btn-teams-xl', 'n_clicks'), Input('btn-teams-sm', 'n_clicks')], 
    [State('modal-teams', 'is_open')],
)(toggle_modal)

app.callback(
    Output('modal-clients', 'is_open'), 
    [Input('btn-clients-xl', 'n_clicks'), Input('btn-clients-sm', 'n_clicks')], 
    [State('modal-clients', 'is_open')],
)(toggle_modal)

app.callback(
    Output('modal-projects', 'is_open'), 
    [Input('btn-projects-xl', 'n_clicks'), Input('btn-projects-sm', 'n_clicks')], 
    [State('modal-projects', 'is_open')],
)(toggle_modal)

app.callback(
    Output('modal-tasks', 'is_open'), 
    [Input('btn-tasks-xl', 'n_clicks'), Input('btn-tasks-sm', 'n_clicks')], 
    [State('modal-tasks', 'is_open')],
)(toggle_modal)


# ==========   Clear Forms Callbacks  ========== #

def clear(n1, n2):
    return [None, False]

app.callback(
    [Output('team-name', 'value'), Output('teams-lockid', 'value')], 
    [Input('modal-teams', 'is_open'), Input('rm-team', 'n_clicks')]
)(clear)

app.callback(
    [Output('client-name', 'value'), Output('clients-lockid', 'value')], 
    [Input('modal-clients', 'is_open'), Input('rm-client', 'n_clicks')]
)(clear)

app.callback(
    [Output('people-name', 'value'), Output('people-lockid', 'value')], 
    [Input('modal-people', 'is_open'), Input('rm-people', 'n_clicks')]
)(clear)

app.callback(
    [Output('project-name', 'value'), Output('projects-lockid', 'value')],
    [Input('modal-projects', 'is_open'), Input('rm-project', 'n_clicks')]
)(clear)

app.callback(
    [Output('task-project', 'value'), Output('tasks-lockid', 'value')], 
    [Input('modal-tasks', 'is_open'), Input('rm-task', 'n_clicks')]
)(clear)

@app.callback(
    [Output('task-people', 'value'), Output('task-name', 'value')], 
    [Input('modal-tasks', 'is_open'), Input('rm-task', 'n_clicks'), 
     Input('unassign-task', 'n_clicks'), Input('task-project-id', 'value')],
)
def clear_tasks(n1, n2, n3, id):
    return [None, None]


# ==========   Update Dropdown Items Callbacks  ========== #

# Teams items

@app.callback(
        Output('teams', 'children'), 
        [Input('rm-team', 'n_clicks'), Input('add-team', 'n_clicks')], 
)
def update_teams_dropdown(n1, n2):
   
    time.sleep(0.5)
    list = update_teams()
    
    if n1 or n2:
        return list
    return list   

# Clients items

@app.callback(
        Output('clients', 'children'), 
        [Input('rm-client', 'n_clicks'), Input('add-client', 'n_clicks')], 
)
def update_clients_dropdown(n1, n2):
   
    time.sleep(0.5)
    list = update_clients()
    
    if n1 or n2:
        return list
    return list   

# People items

@app.callback(
        Output('people', 'children'), 
        [Input('rm-people', 'n_clicks'), Input('add-people', 'n_clicks')], 
)
def update_people_dropdown(n1, n2):
   
    time.sleep(0.5)
    list = update_people()
    
    if n1 or n2:
        return list
    return list   

# Project items

@app.callback(
        Output('projects', 'children'), 
        [Input('rm-project', 'n_clicks'), Input('add-project', 'n_clicks')], 
)
def update_projects_dropdown(n1, n2):
   
    time.sleep(0.5)
    list = update_projects()
    
    if n1 or n2:
        return list
    return list  



# Update taks options after person and project is selected

@app.callback(
    [Output('task-people-id', 'value'), Output('task-assign-dates', 'start_date'), 
     Output('task-assign-dates', 'end_date'), Output('assignment-hours', 'value')],
    [Input('task-people', 'value')],
    [State('task-id', 'value')]
)
def update_task_people(name, task_id):
    
    people = search_people(name)

    if len(people) == 0:
        return [None, None, None, None]

    else:
        people_id = people[0]['id']
        result = search_assign(task_id, people_id)
        
        if len(result) == 0:
            return [people_id, None, None, None]
        
        else:
            assignment = result[0]
            return [people_id, assignment['start_date'], assignment['end_date'], assignment['hours_day']]
        
        return id
    
@app.callback(
    [Output('task-project-id', 'value'), Output('tasks', 'children')],
    [Input('task-project', 'value'), Input('rm-task', 'n_clicks'), 
     Input('add-task', 'n_clicks')],
)
def updatelist_tasks(name, n1, n2):
    
    result = search_project(name)

    if len(result) == 0:
        return [None, None]

    else:
        id = result[0]['id']
        return [id , update_tasks(id)]

# Main function    
 
if __name__ == '__main__':
    app.run_server(port=8090, debug=True)