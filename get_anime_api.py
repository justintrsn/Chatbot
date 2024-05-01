
import requests
from kafka import KafkaProducer
import json
import time
import csv

def get_top_anime(page=1, limit=25):
    url = f"https://api.jikan.moe/v4/top/anime?page={page}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    top_anime = data['data']
    return top_anime

def write_to_csv(anime_list):
    with open('top_anime.csv', 'a', newline='', encoding='utf-8') as csvfile:  # Append mode
        fieldnames = ['Rank', 'Title', 'Score', 'Type', 'Episodes', 'Start Date', 'End Date', 'Members', 'Synopsis', 'Genres']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for anime in anime_list:
            writer.writerow({'Rank': anime['rank'],
                             'Title': anime['title'],
                             'Score': anime['score'],
                             'Type': anime['type'],
                             'Episodes': anime['episodes'],
                             'Genres': ', '.join([genre['name'] for genre in anime['genres']])})

if __name__ == "__main__":
    page = 1
    limit = 25
    while page < 3:
        top_anime = get_top_anime(page, limit)
        if not top_anime:
            break  # No more data available
        write_to_csv(top_anime)
        page += 1
    print("Top anime written to top_anime.csv")

# def create_kafka_producer():
#     return KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))

# def fetch_data_from_jikan(endpoint, limit):
#     data = []
#     page = 1
#     while len(data) < limit:
#         url = f"https://api.jikan.moe/v4/{endpoint}?page={page}&limit=25"
#         response = requests.get(url)
#         if response.status_code == 200:
#             page_data = response.json()['data']
#             data.extend(page_data)
#             page += 1
#         else:
#             print(f"Failed to fetch data for page {page}: {response.status_code}")
#             break
#     return data[:limit]  

# def publish_data(producer, topic, data):
#     for item in data:
#         producer.send(topic, value=item)
#         producer.flush()
#         print(f"Published {item['title']} to {topic}")

# def main():
#     producer = create_kafka_producer()
#     anime_data = fetch_data_from_jikan('top/anime', 100)
#     manga_data = fetch_data_from_jikan('top/manga', 50)

#     publish_data(producer, 'anime_data', anime_data)
#     publish_data(producer, 'manga_data', manga_data)

#     time.sleep(5)  

# if __name__ == "__main__":
#     main()
