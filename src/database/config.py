import streamlit as st
import psycopg2

def run_query(sql, params=None):
    conn = psycopg2.connect(st.secrets["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def run_execute(sql, params=None):
    conn = psycopg2.connect(st.secrets["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    cur.close()
    conn.close()