import requests
import psycopg2
import logging
import time
import sys


# Configure logging to output to STDERR
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

def fetch_data(endpoint, limit, name):
    data = []
    page = 1
    while len(data) < limit:
        url = f"https://api.jikan.moe/v4/{endpoint}?page={page}&limit=25"
        response = requests.get(url)
        if response.status_code == 200:
            page_data = response.json()["data"]
            data.extend(page_data)
            logging.info(f"Fetched {name} page {page}, total items: {len(data)}")
            page += 1
            # time.sleep(1) # Rate limiting on how many request 
        else:
            logging.error(f"Failed to fetch {name} data for page {page}: {response.status_code}")
            break
    return data[:limit]


def create_anime_table(conn):
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

def create_manga_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS manga (
                mal_id SERIAL PRIMARY KEY,
                title TEXT,
                title_english TEXT,
                title_japanese TEXT,
                type TEXT,
                chapters INT,
                volumes INT,
                status TEXT,
                publishing_from_year INT,
                publishing_to_year INT,
                synopsis TEXT,
                genres TEXT,
                themes TEXT,
                demographics TEXT,
                authors TEXT
            );
        """)
        conn.commit()

def insert_manga_data_to_db(connection, data):
    cursor = connection.cursor()
    insert_query = """
    INSERT INTO manga (
        mal_id, title, title_english, title_japanese, type, chapters, volumes,
        status, publishing_from_year, publishing_to_year, synopsis, genres, 
        themes, demographics, authors
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    ) ON CONFLICT (mal_id) DO NOTHING;
    """
    for item in data:
        try:
            cursor.execute(
                insert_query,
                (
                    item["mal_id"],
                    item["title"],
                    item.get("title_english", ""),
                    item.get("title_japanese", ""),
                    item.get("type", ""),
                    item.get("chapters", 0),
                    item.get("volumes", 0),
                    item.get("status", ""),
                    item["published"]["from"]["year"] if "published" in item and "from" in item["published"] else None,
                    item["published"]["to"]["year"] if "published" in item and "to" in item["published"] else None,
                    item.get("synopsis", ""),
                    ", ".join([genre["name"] for genre in item["genres"]]),
                    ", ".join([theme["name"] for theme in item["themes"]]),
                    ", ".join([demo["name"] for demo in item["demographics"]]),
                    ", ".join([author["name"] for author in item["authors"]])
                )
            )
        except Exception as e:
            logging.error(f"Error inserting manga: {item['title']}. Error: {e}")
    connection.commit()
    cursor.close()

def insert_anime_data_to_db(connection, data):
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
    create_anime_table(connection)
    create_manga_table(connection)
    logging.info("Created tables")
    try:
        # Fetch and load dataset
        anime_data = fetch_data("top/anime", 1000, "anime")
        manga_data = fetch_data("top/manga", 500, "manga")
        insert_anime_data_to_db(connection, anime_data)
        insert_manga_data_to_db(connection, manga_data)
        logging.info("Database initialized")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
