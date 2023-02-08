CREATE SINK CONNECTOR SINK_ES_AGG WITH (
    'connector.class' = 'io.confluent.connect.elasticsearch.ElasticsearchSinkConnector',
    'topics'          = 'ORDERS_BY_HOUR',
    'connection.url'  = 'http://elasticsearch:9200',
    'type.name'       = 'type.name=kafkaconnect',
    'key.ignore'      = 'false',
    'schema.ignore'   = 'true'
);