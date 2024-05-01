import requests
import psycopg2
import json


def fetch_data(endpoint, limit):
    data = []
    page = 1
    while len(data) < limit:
        url = f"https://api.jikan.moe/v4/{endpoint}?page={page}&limit=25"
        response = requests.get(url)
        if response.status_code == 200:
            page_data = response.json()["data"]
            data.extend(page_data)
            page += 1
        else:
            print(f"Failed to fetch data for page {page}: {response.status_code}")
            break
    return data[:limit]


def insert_data_to_db(connection, data, table):
    cursor = connection.cursor()
    insert_query = f"""
    INSERT INTO {table} (
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
    try:
        # Fetch and load dataset
        anime_data = fetch_data("top/anime", 50)
        insert_data_to_db(connection, anime_data, "anime_dataset")
        manga_data = fetch_data("top/manga", 50)
        insert_data_to_db(connection, manga_data, "manga_dataset")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
