CREATE STREAM readings (
    sensor VARCHAR KEY,
    location VARCHAR,
    reading INT
) WITH (
    KAFKA_TOPIC = 'readings',
    PARTITIONS = 3,
    VALUE_FORMAT = 'json'
);

/* 
Populate stream
SQL users will instantly recognize that we use standard INSERT statements to add data to the stream.
Again, no knowledge of stream management, topics, partitions, etc.,
is needed for a developer to start adding data into these streams.
*/

INSERT INTO readings (sensor, location, reading) VALUES ('sensor-1', 'wheel', 45);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-2', 'motor', 41);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-1', 'wheel', 42);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-3', 'muffler', 42);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-3', 'muffler', 40);
 
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-4', 'motor', 43);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-6', 'muffler', 43);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-5', 'wheel', 41);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-5', 'wheel', 42);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-4', 'motor', 41);
 
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-7', 'muffler', 43);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-8', 'wheel', 40);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-9', 'motor', 40);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-9', 'motor', 44);
INSERT INTO readings (sensor, location, reading) VALUES ('sensor-7', 'muffler', 41);

/*
Filtering Rows out of a Stream
*/

CREATE STREAM high_pri AS
    SELECT sensor,
           reading,
           UCASE(location) AS location
    FROM readings
    WHERE reading > 41
    EMIT CHANGES; 