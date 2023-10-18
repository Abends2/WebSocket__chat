import asyncpg
import hashlib, uuid
import hashlib


DATABASE_URL = 'postgresql://postgres:postgres@0.0.0.0:5432/chat'


#===================================================

def create_passwd(plain_text_password: str) -> str:
    return hashlib.sha256(plain_text_password.encode('utf-8')).hexdigest()

def auth_passwd(password: str, submit_password: str) -> str:
    if password == hashlib.sha256(submit_password.encode('utf-8')).hexdigest():
        return True
    else:
        return False

#===================================================

async def create_tables():
    # Create users table
    await conn.execute('''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            token VARCHAR(255)
        );
    ''')
    
    # Create files table
    await conn.execute('''
        CREATE TABLE files (
            id SERIAL PRIMARY KEY,
            path VARCHAR(255) NOT NULL
        );
    ''')
    
    # Create messages table
    await conn.execute('''
        CREATE TABLE messages (
            id SERIAL PRIMARY KEY,
            room_id INTEGER NOT NULL,
            message TEXT,
            file_id INTEGER,
            date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_edit TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES files(id)
        );
    ''')

    await conn.close()

#===================================================

async def register(username: str, password: str):
    conn = await asyncpg.connect(DATABASE_URL)
    hashed_password = create_passwd(password)

    rows = await conn.fetch('''
        SELECT username FROM users;
    ''')
    rows = [row['username'] for row in rows]


    if username in rows:
        return False, "user already registered"
    await conn.execute('''
        INSERT INTO users (username, password) VALUES ($1, $2);
    ''', username, hashed_password)
    return True, "ok"

#===================================================

async def login(username: str, password: str):
    conn = await asyncpg.connect(DATABASE_URL)
    hashed_password = create_passwd(password)
    row = await conn.fetch('''
        SELECT username, password FROM users WHERE username = $1;
    ''', username)

    if auth_passwd(row[0]["password"], password):
        new_token = str(uuid.uuid4())

        await conn.execute('''
            UPDATE users SET token = $1 WHERE username = $2;
        ''', new_token, username)

        return True, new_token

    else:
        return False, "bad creds"

#===================================================

async def check_token(token_in):
    conn = await asyncpg.connect(DATABASE_URL)
    tokens = await conn.fetch('''
        SELECT token FROM users;
    ''')
    tokens = [row['token'] for row in tokens]
    if token_in in tokens:
        return True
    else:
        return False

#===================================================

async def save_message(message):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
        INSERT INTO messages (message) VALUES ($1);
    ''', message)
    await conn.close()
    return True

#===================================================

async def rooms():
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch('''
        SELECT room_id FROM messages;
    ''')
    rows = [row['room_id'] for row in rows]
    await conn.close()
    return rows

#===================================================

async def update_token_for_user(conn, username: str):
    await conn.execute('''
        UPDATE users SET token = $1 WHERE username = $2;
    ''', new_token, username)

    return new_token

#===================================================