

CREATE TABLE users (
    id serial PRIMARY KEY,
    firstname TEXT NOT NULL, 
    lastname TEXT NOT NULL, 
    email TEXT NOT NULL UNIQUE, 
    password TEXT NOT NULL,
    admin BOOLEAN NOT NULL 
);

CREATE TABLE presence (
    id serial PRIMARY KEY,
    userid INTEGER NOT NULL, 
    date DATE NOT NULL, 
    scannedat TIMESTAMP, 
    FOREIGN KEY (userid) REFERENCES users (id)
);

CREATE TABLE temp_codes (
    id serial PRIMARY KEY,
    code TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL
);

CREATE TABLE code_usage (
    id serial PRIMARY KEY,
    code_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (code_id) REFERENCES temp_codes (id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (code_id, user_id)  
);
