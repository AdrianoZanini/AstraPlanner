CREATE TABLE Clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    email TEXT
);

CREATE TABLE Teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE People (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    team_id INTEGER NOT NULL,
    phone TEXT,
    FOREIGN KEY (team_id) REFERENCES Teams(id)
);

CREATE TABLE Projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    client_id INTEGER NOT NULL,
    due_date DATE NOT NULL,
    done BOOLEAN DEFAULT 0,
    FOREIGN KEY (client_id) REFERENCES Clients(id)
);

CREATE TABLE Tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    project_id INTEGER NOT NULL,
    due_date DATE NOT NULL,
    demand INTEGER NOT NULL,
    done BOOLEAN DEFAULT 0,
    FOREIGN KEY (project_id) REFERENCES Projects(id)
);

CREATE TABLE TaskAssign (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    date_time DATETIME,
    task_id INTEGER NOT NULL,
    people_id INTEGER NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    hours_day INTEGER NOT NULL,
    total_hours INTEGER NOT NULL,
    FOREIGN KEY (people_id) REFERENCES People(id),
    FOREIGN KEY (task_id) REFERENCES Tasks(id)
);
