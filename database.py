import os
import hashlib
import pymysql
from pymysql.cursors import DictCursor

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345")
DB_NAME = os.getenv("DB_NAME", "placement_portal")
DB_PORT = int(os.getenv("DB_PORT", 3308))


def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=DictCursor,
        charset="utf8mb4",
        autocommit=False,
    )


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_tables():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                company VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                job_id INT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_application (user_id, job_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        return cur.fetchone()
    finally:
        conn.close()


def create_user(name: str, email: str, password: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
            (name, email, password)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_jobs():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs ORDER BY id DESC")
        return cur.fetchall()
    finally:
        conn.close()


def create_job(title: str, company: str, description: str):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO jobs(title,company,description) VALUES(%s,%s,%s)",
            (title, company, description)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def has_applied(user_id: int, job_id: int) -> bool:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM applications WHERE user_id=%s AND job_id=%s",
            (user_id, job_id)
        )
        return cur.fetchone() is not None
    finally:
        conn.close()


def add_application(user_id: int, job_id: int) -> bool:
    if has_applied(user_id, job_id):
        return False

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO applications(user_id,job_id) VALUES(%s,%s)",
            (user_id, job_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()
