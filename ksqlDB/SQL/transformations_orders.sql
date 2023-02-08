CREATE OR REPLACE STREAM ORDERS_PORTUGUES WITH (KAFKA_TOPIC='ORDERS_PORTUGUES', VALUE_FORMAT='AVRO')
AS SELECT ID as `ID`,
    CASE
        WHEN MAKE='GMC' THEN 'General Motors'
        WHEN MAKE='Ford' THEN 'Ford Motor Company'
        ELSE MAKE
    END AS FABRICANTE,

    CUSTOMER_ID AS CLIENTE_ID,
    ORDER_TOTAL_USD AS VALOR_TOTAL_USD,
    MODEL AS MODELO,
    DELIVERY_CITY AS CIUDAD_ENTREGA,
    DELIVERY_COMPANY AS EMPRESA_ENTREGA,
    CREATE_TS AS FECHA_CREACION,
    UPDATE_TS AS FECHA_ACTUALIZACION,

    CASE
        WHEN LEN(REGEXP_EXTRACT('[0-9]{2}/[0-9]{2}/[0-9]{4}', CREATE_TS))>0 
        THEN PARSE_DATE(CREATE_TS, 'dd''/''MM''/''yyyy')
        WHEN LEN(REGEXP_EXTRACT('[0-9]{2}/[0-9]{2}/[0-9]{2}', CREATE_TS))>0 
        THEN PARSE_DATE(CREATE_TS, 'dd''/''MM''/''yy')
        WHEN LEN(REGEXP_EXTRACT('[0-9]{4}-[0-9]{2}-[0-9]{2}', CREATE_TS))>0 
        THEN PARSE_DATE(CREATE_TS, 'yyyy-MM-dd ')
        ELSE NULL
    END AS `date`
FROM
ORDERS;


CREATE OR REPLACE TABLE ORDERS_MONTHLY_AGG WITH (KAFKA_TOPIC='ORDERS_TRANSFORMED', VALUE_FORMAT='AVRO')
AS SELECT FORMAT_DATE(`date`, 'yyyy-MM') AS `ID`,

    -- Absolute numbers
    COUNT(*) AS TOTAL_ORDERS,
    SUM(VALOR_TOTAL_USD) AS TOTAL_USD,

    -- percentual numbers
    AVG(VALOR_TOTAL_USD) * 100 AS VALOT_TOTAL_PERCENT,
    COUNT(*) * 100 / (SELECT COUNT(*) FROM ORDERS_TRANSFORMED) AS TOTAL_ORDERS_PERCENT,
    SUM(VALOR_TOTAL_USD) * 100 / (SELECT SUM(VALOR_TOTAL_USD) FROM ORDERS_TRANSFORMED) AS TOTAL_USD_PERCENT
 
    AVG(
        CASE
            WHEN MODELO='Toyota' THEN 1
            ELSE 0
        END
    ) AS PERCENTUAL_TOYOTA,

    AVG(
        CASE
            WHEN MODELO='Honda' THEN 1
            ELSE 0
        END
    ) AS PERCENTUAL_HONDA,

    AVG(
        CASE
            WHEN MODELO='Ford Motor Company' THEN 1
            ELSE 0
        END
    ) AS PERCENTUAL_FORD,

FROM
    ORDERS_PORTUGUES
GROUP BY FORMAT_DATE(`date`, 'yyyy-MM')
EMIT CHANGES;

CREATE TABLE AVERAGE_ORDER_VALUE WITH (KAFKA_TOPIC='AVERAGE_ORDER_VALUE', VALUE_FORMAT='AVRO')
AS 
    SELECT FABRICANTE, AVG(VALOR_TOTAL_USD) AS USD_RATE
    FROM ORDERS_PORTUGUES
    GROUP BY FABRICANTE
EMIT CHANGES;