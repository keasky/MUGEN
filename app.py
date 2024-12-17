from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理用

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    conn = get_db_connection()
    conn.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()
    session['username'] = username
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    username = session.get('username')
    if not username:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # アクティブな他のユーザーを探す
    cursor.execute("SELECT * FROM users WHERE username != ? AND is_active = 1", (username,))
    users = cursor.fetchall()

    if users:
        # ランダムに他のユーザーとマッチング
        partner = random.choice(users)
        
        # ルームを作成
        cursor.execute("INSERT INTO chat_rooms (user1_id, user2_id) VALUES ((SELECT id FROM users WHERE username = ?), ?)",
                       (username, partner['id']))
        conn.commit()
        room_id = cursor.lastrowid
        conn.close()
        
        return render_template('chat.html', room_id=room_id, partner_name=partner['username'])
    else:
        return "他にアクティブなユーザーがいません。"

if __name__ == '__main__':
    app.run(debug=True)
