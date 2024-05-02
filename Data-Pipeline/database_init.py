import requests
import psycopg2
import logging
import time
import sys


# Configure logging to output to STDERR
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def fetch_data(endpoint, limit):
    data = []
    page = 1
    while len(data) < limit:
        url = f"https://api.jikan.moe/v4/{endpoint}?page={page}&limit=25"
        response = requests.get(url)
        if response.status_code == 200:
            page_data = response.json()["data"]
            data.extend(page_data)
            logging.info(f"Fetched page {page}, total items: {len(data)}")
            page += 1
            time.sleep(1) # Rate limiting on how many request 
        else:
            logging.error(f"Failed to fetch data for page {page}: {response.status_code}")
            break
    return data[:limit]


def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS animes (
                mal_id SERIAL PRIMARY KEY,
                title TEXT,
                title_english TEXT,
                title_synonyms TEXT,
                type TEXT,
                status TEXT,
                synopsis TEXT,
                rating TEXT,
                year INT,
                genres TEXT,
                demographics TEXT,
                themes TEXT    
            );
        """)
        conn.commit()

def insert_data_to_db(connection, data):
    cursor = connection.cursor()
    insert_query = f"""
    INSERT INTO animes (
        mal_id, title, title_english, title_synonyms, type, status, synopsis, genres, demographics, themes
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    ) ON CONFLICT (mal_id) DO NOTHING;
    """
    for item in data:
        try:
            cursor.execute(
                insert_query,
                (
                    item["mal_id"],
                    item["title"],
                    item["title_english"],
                    ", ".join(item["title_synonyms"]),
                    item["type"],
                    item["status"],
                    item["synopsis"].replace('\n', ' ').replace('\r', '').replace('"', "'"),
                    ", ".join([genre["name"] for genre in item["genres"]]),
                    ", ".join([demo["name"] for demo in item["demographics"]]),
                    ", ".join([theme["name"] for theme in item["themes"]]),
                )
            )
        except Exception as e:
            print(f"Error inserting item: {item['title']}. Error: {e}")
    connection.commit()
    cursor.close()

def main():
    connection = psycopg2.connect(
        user= "postgres",
        password= "secret",
        host= "postgres",
        port= "5432",
        database= "animanga_database",
    )
    create_table(connection)
    logging.info("Created tables")
    try:
        # Fetch and load dataset
        anime_data = fetch_data("top/anime", 1500)
        insert_data_to_db(connection, anime_data)
        logging.info("Database initialized")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
