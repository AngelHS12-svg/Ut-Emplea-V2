from app.config.database import get_connection


def main():
    conn = get_connection()
    try:
        print("Conexión exitosa a PostgreSQL")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
