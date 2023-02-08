## KafkaConsumer

`KafkaConsumer` is a high-level message consumer, intended to operate as similarly as possible to the official java client.

See `KafkaConsumer` for API and configuration details.

The consumer iterator returns `ConsumerRecords`, which are simple named tuples that expose basic message attributes: `topic`, `partition`, `offset`, `key`, and `value`:
