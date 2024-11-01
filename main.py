import json
from confluent_kafka import Consumer, KafkaError
import psycopg2

consumer_conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "cdc_group",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(consumer_conf)
consumer.subscribe(["dbserver1.public.table_A"])

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port=5435,
)
cursor = conn.cursor()


def process_message(message):
    event = json.loads(message.value().decode("utf-8"))
    print(event, "eventtttttttt")
    return

    payload = event["payload"]
    op_type = payload["op"]  # 'c' for create, 'u' for update, 'd' for delete

    # Map Debezium operations to SQL
    if op_type == "c":  # Insert
        data = payload["after"]
        cursor.execute(
            "INSERT INTO employees (id, name, position, salary) VALUES (%s, %s, %s, %s)",
            (data["id"], data["name"], data["position"], data["salary"]),
        )
    elif op_type == "u":  # Update
        data = payload["after"]
        cursor.execute(
            "UPDATE employees SET name = %s, position = %s, salary = %s WHERE id = %s",
            (data["name"], data["position"], data["salary"], data["id"]),
        )
    elif op_type == "d":  # Delete
        data = payload["before"]
        cursor.execute("DELETE FROM employees WHERE id = %s", (data["id"],))

    # Commit changes to Database B
    conn.commit()


# Consume messages
try:
    while True:
        msg = consumer.poll(1.0)
        print(msg, "hereeeeee")

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"End of partition reached {msg.topic()}/{msg.partition()}")
            else:
                print(f"Error: {msg.error()}")
            continue

        process_message(msg)

except KeyboardInterrupt:
    print("error 11111111")

except Exception:
    print("error 22222222")

finally:
    # Cleanup
    consumer.close()
    cursor.close()
    conn.close()
