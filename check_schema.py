import psycopg2
import os

def check_schema():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "bolsa_trabajo_uto"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", "angel123"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        
        print("--- SCHEMA: candidatos ---")
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'candidatos'
            ORDER BY ordinal_position;
        """)
        for row in cur.fetchall():
            print(f"Column: {row[0]:<20} | Type: {row[1]:<15} | Length: {row[2]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
