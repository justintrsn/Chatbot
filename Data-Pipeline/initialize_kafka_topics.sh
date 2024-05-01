#!/bin/bash
KAFKA_BROKER="kafka:9092"

# Create topics
kafka-topics.sh --create --if-not-exists --bootstrap-server $KAFKA_BROKER --partitions 1 --replication-factor 1 --topic anime_data
kafka-topics.sh --create --if-not-exists --bootstrap-server $KAFKA_BROKER --partitions 1 --replication-factor 1 --topic manga_data

# Verify
kafka-topics.sh --list --bootstrap-server $KAFKA_BROKER
echo "Created kafka topics successfully"