# flake8: noqa E501
from kafka import KafkaConsumer
import json
import psycopg2
from psycopg2 import sql

# Kafka config
BOOTSTRAP_SERVERS = "localhost:9092"
TOPICS = ["dbserver1.public.table_b", "dbserver1.public.table_c"]

# Database config
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": 5435,
}

# Initialize Kafka Consumer for both topics
consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="consumer_group",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)


def _get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def _upsert_record(cursor, table_name, data):
    query_check = sql.SQL("SELECT EXISTS(SELECT 1 FROM {table} WHERE id = %s)").format(
        table=sql.Identifier(table_name)
    )
    cursor.execute(query_check, (data["id"],))
    exists = cursor.fetchone()[0]

    if exists:
        query_update = sql.SQL(
            "UPDATE {table} SET first_name = %s, last_name = %s WHERE id = %s"
        ).format(table=sql.Identifier(table_name))
        cursor.execute(
            query_update, (data["first_name"], data["last_name"], data["id"])
        )
        print(f"Updated record in {table_name}: {data}")

    else:
        query_insert = sql.SQL(
            "INSERT INTO {table} (id, first_name, last_name) VALUES (%s, %s, %s)"
        ).format(table=sql.Identifier(table_name))
        cursor.execute(
            query_insert, (data["id"], data["first_name"], data["last_name"])
        )
        print(f"Inserted new record into {table_name}: {data}")


def _process_message(message):
    payload = message.value
    print(f"Received message from {message.topic} - payload: {payload}")

    if payload["op"] != "u":  # 'c' for create, 'u' for update, 'd' for delete
        return

    table_name = message.topic.split(".")[-1]
    data = payload.get("after")

    if data:
        with _get_db_connection() as conn:
            with conn.cursor() as cursor:
                _upsert_record(cursor, table_name, data)
            conn.commit()


def main():
    print("Starting Kafka Consumer...")
    for message in consumer:
        _process_message(message)
        consumer.commit()


if __name__ == "__main__":
    main()
