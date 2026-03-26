import sqlite3
import os
from datetime import datetime

DB_PATH = "trading.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 交易紀錄表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            time        TEXT    NOT NULL,
            action      TEXT    NOT NULL,
            stock_id    TEXT    NOT NULL,
            shares      INTEGER NOT NULL,
            price       REAL    NOT NULL,
            amount      REAL    NOT NULL
        )
    """)

    # 帳戶狀態表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS account (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            cash         REAL    NOT NULL,
            initial_cash REAL    NOT NULL,
            updated_at   TEXT    NOT NULL
        )
    """)

    # 持股明細表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS holdings (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id  TEXT NOT NULL UNIQUE,
            shares    INTEGER NOT NULL,
            avg_cost  REAL    NOT NULL,
            updated_at TEXT   NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("  [資料庫] 初始化完成")


def save_trade(action, stock_id, shares, price):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trades (time, action, stock_id, shares, price, amount)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        action, stock_id, shares, price,
        round(shares * price, 2)
    ))
    conn.commit()
    conn.close()


def save_account(cash, initial_cash):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM account")
    cursor.execute("""
        INSERT INTO account (cash, initial_cash, updated_at)
        VALUES (?, ?, ?)
    """, (cash, initial_cash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def save_holdings(holdings):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM holdings")
    for stock_id, info in holdings.items():
        cursor.execute("""
            INSERT INTO holdings (stock_id, shares, avg_cost, updated_at)
            VALUES (?, ?, ?, ?)
        """, (
            stock_id, info["shares"], info["avg_cost"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
    conn.commit()
    conn.close()


def load_account():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM account ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"cash": row["cash"], "initial_cash": row["initial_cash"]}
    return None


def load_holdings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM holdings")
    rows = cursor.fetchall()
    conn.close()
    holdings = {}
    for row in rows:
        holdings[row["stock_id"]] = {
            "shares": row["shares"],
            "avg_cost": row["avg_cost"]
        }
    return holdings


def load_trades():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
