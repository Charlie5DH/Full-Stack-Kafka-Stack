/*
We want to model a stream of credit card transactions from which we'll look for anomalous activity. 
To do that, create a ksqlDB stream to represent the transactions. 
Each transaction has a few key pieces of information, like the card number, amount, and email address that it's associated with. 
Because the specified topic (transactions) does not exist yet, ksqlDB creates it on your behalf.
*/

CREATE STREAM transactions (
    tx_id VARCHAR KEY,
    email_address VARCHAR,
    card_number VARCHAR,
    timestamp VARCHAR,
    amount DECIMAL(12, 2)
) WITH (
    kafka_topic = 'transactions',
    partitions = 8,
    value_format = 'avro',
    timestamp = 'timestamp',
    timestamp_format = 'yyyy-MM-dd''T''HH:mm:ss'
);

/*
Notice that this stream is configured with a custom timestamp to signal that event-time should be used instead of processing-time. 
What this means is that when ksqlDB does time-related operations over the stream, it uses the timestamp column to measure time, 
not the current time of the operating system. This makes it possible to handle out-of-order events.

The stream is also configured to use the Avro format for the value part of the underlying Kafka records that it generates. 
Because ksqlDB has been configured with Schema Registry (as part of the Docker Compose file), the schemas of each stream and table are centrally tracked. 
We'll make use of this in our microservice later.
*/

/*
If a single credit card is transacted many times within a short duration, there's probably something suspicious going on. 
A table is an ideal choice to model this because you want to aggregate events over time and find activity that spans multiple events. 
Run the following statement:
*/

CREATE TABLE possible_anomalies WITH (
    kafka_topic = 'possible_anomalies',
    VALUE_AVRO_SCHEMA_FULL_NAME = 'io.ksqldb.tutorial.PossibleAnomaly'
)   AS
    SELECT card_number AS `card_number_key`,
           as_value(card_number) AS `card_number`,
           latest_by_offset(email_address) AS `email_address`,
           count(*) AS `n_attempts`,
           sum(amount) AS `total_amount`,
           collect_list(tx_id) AS `tx_ids`,
           WINDOWSTART as `start_boundary`,
           WINDOWEND as `end_boundary`
    FROM transactions
    WINDOW TUMBLING (SIZE 30 SECONDS, RETENTION 1000 DAYS)
    GROUP BY card_number
    HAVING count(*) >= 3
    EMIT CHANGES;


/*
Here's what this statement does:

For each credit card number, 30 second tumbling windows are created to group activity. 
A new row is inserted into the table when at least 3 transactions take place inside a given window.

The window retains data for the last 1000 days based on each row's timestamp. 
In general, you should choose your retention carefully. It is a trade-off between storing data longer and having larger state sizes. 
The very long retention period used in this tutorial is useful because the timestamps are fixed at the time of writing this and won't
need to be adjusted often to account for retention.

The credit card number is selected twice. In the first instance, it becomes part of the underlying Kafka record key,
because it's present in the group by clause, which is used for sharding. 
In the second instance, the as_value function is used to make it available in the value, too. This is generally for convenience.

The individual transaction IDs and amounts that make up the window are collected as lists.

The last transaction's email address is "carried forward" with latest_by_offset.

Column aliases are surrounded by backticks, which tells ksqlDB to use exactly that case. ksqlDB uppercases identity names by default.

The underlying Kafka topic for this table is explicitly set to possible_anomalies.

The Avro schema that ksqlDB generates for the value portion of its records is recorded under the namespace io.ksqldb.tutorial.PossibleAnomaly. 
You'll use this later in the microservice.
*/
