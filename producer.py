from kafka import KafkaConsumer, KafkaProducer
import json

# Kafka config
BOOTSTRAP_SERVERS = "localhost:9092"
INPUT_TOPIC = "table_a"
TOPIC_PREFIX = "dbserver1"

# Topic routing
TOPIC_MAPPING = {
    "table_b": f"{TOPIC_PREFIX}.public.table_b",
    "table_c": f"{TOPIC_PREFIX}.public.table_c",
}

# Initialize Kafka Consumer and Producer
consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="cdc_group",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)


def _get_target_topic(record):
    last_name = record["after"].get("last_name", "").lower()
    for keyword, topic in TOPIC_MAPPING.items():
        if keyword in last_name:
            return topic

    return f"{TOPIC_PREFIX}.public.table_a"


def _process_message(record):
    target_topic = _get_target_topic(record)
    producer.send(target_topic, record)
    producer.flush()
    print(f"Record sent to {target_topic}")


def main():
    print("Starting Kafka Producer...")
    for message in consumer:
        record = message.value
        print(f"Received message: {record}")
        _process_message(record)


if __name__ == "__main__":
    main()
