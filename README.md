## Change Data Capture (CDC) with Debezium, PostgreSQL, and Kafka

### Start the docker services

```bash
# Start docker
docker-compose up -d

# Clean Up
docker-compose down
```

### Setup the Debezium PostgreSQL connector:

```bash
# Deploy the connector:
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://localhost:8083/connectors/ -d @register-postgres.json

# Verify that the connector is deployed:
curl -s -XGET http://localhost:8083/connector-plugins | jq '.[].class'
```

### Database Setup

1. Access PostgreSQL:

   ```bash
   docker-compose exec postgres bash -c 'psql -U $POSTGRES_USER postgres'
   ```

2. Create tables `table_a`, `table_b`, and `table_c`:

   ```sql
   CREATE TABLE table_a (
       id INT PRIMARY KEY,
       first_name VARCHAR(50),
       last_name VARCHAR(50)
   );

   CREATE TABLE table_b (
       id INT PRIMARY KEY,
       first_name VARCHAR(50),
       last_name VARCHAR(50)
   );

   CREATE TABLE table_c (
       id INT PRIMARY KEY,
       first_name VARCHAR(50),
       last_name VARCHAR(50)
   );
   ```

3. Insert sample data:

   ```sql
   INSERT INTO table_a VALUES (1, 'name_1', 'last_1');
   INSERT INTO table_a VALUES (2, 'name_2', 'last_2');
   INSERT INTO table_a VALUES (3, 'name_3', 'last_3');

   INSERT INTO table_b VALUES (1, 'name_1', 'last_1');
   INSERT INTO table_b VALUES (2, 'name_2', 'last_2');
   INSERT INTO table_b VALUES (3, 'name_3', 'last_3');

   INSERT INTO table_c VALUES (1, 'name_1', 'last_1');
   INSERT INTO table_c VALUES (2, 'name_2', 'last_2');
   INSERT INTO table_c VALUES (3, 'name_3', 'last_3');
   ```

4. Verify table content:
   ```sql
   SELECT * FROM table_a;
   SELECT * FROM table_b;
   SELECT * FROM table_c;
   ```

### Kafka Topic Consumption

Consume data from Kafka topics for each table to verify the CDC changes.

```bash
kafka-console-consumer --bootstrap-server localhost:9092 --from-beginning --property print.key=false --topic dbserver1.public.table_a | jq
kafka-console-consumer --bootstrap-server localhost:9092 --from-beginning --property print.key=false --topic dbserver1.public.table_b | jq
kafka-console-consumer --bootstrap-server localhost:9092 --from-beginning --property print.key=false --topic dbserver1.public.table_c | jq
```

### Run custom Kafka producers and consumers:

```bash
# Run the producer
python producer.py

# Run the consumer
python consumer.py
```

### Update table_a manually to Trigger CDC

```sql
UPDATE table_a SET last_name = 'BAO_table_b' WHERE id = 2;
UPDATE table_a SET last_name = 'BAO_table_c' WHERE id = 3;
```

These updates should automatically sync to table_b and table_c based on the CDC configuration.

---

### Resources

- [Debezium Architecture Documentation](https://debezium.io/documentation/reference/3.0/architecture.html)
- [Debezium Connector for PostgreSQL](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#debezium-postgresql-connector-kafka-signals-configuration-properties)
- [Kafka Tool - UI for Kafka](https://www.kafkatool.com/download.html)

---

### TODO

- [ ] Add CRUD operation scenarios to test more complex CDC behaviors.
- [ ] Experiment with multi-table joins and complex transformations in CDC.
