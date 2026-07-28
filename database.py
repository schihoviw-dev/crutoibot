# database.py
import sqlite3
import random
import string

DB_NAME = "scam_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            successful_deals INTEGER DEFAULT 0,
            rating REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requisites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT CHECK(type IN ('gram', 'card', 'stars')),
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            deal_code TEXT PRIMARY KEY,
            seller_id INTEGER,
            buyer_id INTEGER,
            currency TEXT CHECK(currency IN ('GRAM', 'Звёзды')),
            amount REAL,
            description TEXT,
            status TEXT DEFAULT 'created',
            commission REAL DEFAULT 3.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            paid_at TIMESTAMP,
            confirmed_at TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def generate_deal_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def add_user(user_id, username, full_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)", 
                (user_id, username, full_name))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

def update_user_successful_deals(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET successful_deals = successful_deals + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def add_requisite(user_id, req_type, value):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO requisites (user_id, type, value) VALUES (?, ?, ?)", 
                (user_id, req_type, value))
    conn.commit()
    conn.close()

def get_requisites(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT type, value FROM requisites WHERE user_id = ?", (user_id,))
    reqs = cur.fetchall()
    conn.close()
    return reqs

def delete_requisites(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM requisites WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def create_deal(seller_id, currency, amount, description):
    code = generate_deal_code()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO deals (deal_code, seller_id, currency, amount, description)
        VALUES (?, ?, ?, ?, ?)
    """, (code, seller_id, currency, amount, description))
    conn.commit()
    conn.close()
    return code

def get_deal(deal_code):
    clean_code = deal_code.replace('#', '')
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM deals WHERE deal_code = ?", (clean_code,))
    deal = cur.fetchone()
    conn.close()
    return deal

def update_deal_buyer(deal_code, buyer_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE deals SET buyer_id = ?, status = 'joined' WHERE deal_code = ?", 
                (buyer_id, deal_code))
    conn.commit()
    conn.close()

def update_deal_paid(deal_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE deals SET status = 'paid', paid_at = CURRENT_TIMESTAMP WHERE deal_code = ?", 
                (deal_code,))
    conn.commit()
    conn.close()

def update_deal_confirmed(deal_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE deals SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP WHERE deal_code = ?", 
                (deal_code,))
    conn.commit()
    conn.close()

def update_deal_completed(deal_code):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE deals SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE deal_code = ?", 
                (deal_code,))
    conn.commit()
    conn.close()

def get_user_deals(user_id, status=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if status:
        cur.execute("SELECT * FROM deals WHERE (seller_id = ? OR buyer_id = ?) AND status = ?", 
                    (user_id, user_id, status))
    else:
        cur.execute("SELECT * FROM deals WHERE seller_id = ? OR buyer_id = ?", 
                    (user_id, user_id))
    deals = cur.fetchall()
    conn.close()
    return deals

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    conn.close()
    return users

def get_all_deals():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM deals ORDER BY created_at DESC")
    deals = cur.fetchall()
    conn.close()
    return deals

def get_deal_count_by_status():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT status, COUNT(*) FROM deals GROUP BY status")
    stats = cur.fetchall()
    conn.close()
    return stats

def get_user_count():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()
    return count