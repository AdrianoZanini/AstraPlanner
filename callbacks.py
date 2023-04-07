@app.callback(
        [Output('teams-alert', 'children'), Output('teams-alert', 'is_open'), 
         Output('teams-alert', 'color'), Output('rm-team-name', 'options')], 
        [Input("add-team", "n_clicks"), Input("rm-team", "n_clicks")], 
        [State('teams-alert', 'is_open'), State('add-team-name','value'), State('rm-team-name','value')]
)
def teams_edit(btn1, btn2, is_open, add_name, rm_name):

    message=[]

    if btn1 or btn2 is None:
        raise PreventUpdate
    elif btn1: 
        if add_name == "":
            message = "Name must not be blank"
            color="danger"
        if add_name in teams:
            message = "Team already exists"
            color="danger"
        else:
            db.execute("INSERT INTO teams (name) VALUES (?)", add_name)
            message = "Team Added"
            color="success"
    elif btn2:
        if rm_name == "":
            message = "Team must not be blank"
            color="danger"
        else:
            db.execute("DELETE FROM teams WHERE name = ?", rm_name)
            message = "Team Removed"
            color="success"
    
    teams = update_teams()

    return [message, not is_open, color, teams]

@app.callback(
        [Output('clients-alert', 'children'), Output('clients-alert', 'is_open'), 
         Output('clients-alert', 'color'), Output('rm-client-name', 'options')], 
        [Input("add-client", "n_clicks"), Input("rm-client", "n_clicks")], 
        [State('clients-alert', 'is_open'), State('add-client-name','value'), 
         State('add-client-email','value'), State('add-client-phone','value'), State('rm-client-name','value')]
)
def clients_edit(n1, n2, is_open, add_name, add_email, add_phone, rm_name):

    if n1 or n2 is None:
        raise PreventUpdate
    elif n1: 
        if add_name == "":
            message = "Name must not be blank"
            color="danger"
        if add_name in clients:
            message = "client already exists"
            color="danger"
        else:
            db.execute("INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)", add_name, add_email, add_phone)
            message = "client Added"
            color="success"
    elif n2:
        if rm_name == "":
            message = "Client must not be blank"
            color="danger"
        else:
            db.execute("DELETE FROM clients WHERE name = ?", rm_name)
            message = "Client Removed"
            color="success"
    
    clients = update_clients()

    return [message, not is_open, color, clients]

def clear(n):
    return ""

app.callback(
    Output("add-team-name", "value"), Input("modal-teams", "is_open")
)(clear)

app.callback(
    Output("rm-team-name", "value"), Input("modal-teams", "is_open")
)(clear)
