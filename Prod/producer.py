#!/usr/bin/env python

import pika, sys, json
from flask import Flask, request, jsonify

connection = pika.BlockingConnection(parameters= pika.ConnectionParameters(host='rabbitmq'))

channel_health_check = connection.channel()
channel_insertion = connection.channel()
channel_deletion = connection.channel()
channel_read = connection.channel()

channel_health_check.queue_declare(queue='health_check', durable=True)
channel_insertion.queue_declare(queue='insert_record', durable=True)
channel_deletion.queue_declare(queue='delete_record', durable=True)
channel_read.queue_declare(queue='read_database', durable=True)

app = Flask(__name__)
# app.debug = True

@app.route("/", methods = ["GET"])
def routes():
    message = {
        "to health check": "http://127.0.0.1:8000/health-check",
        "to read data": "http://127.0.0.1:8000/read-database",
        "to insert data": "http://127.0.0.1:8000/insert-record",
        "to delete data": "http://127.0.0.1:8000/delete-record"
    }
    
    return json.dumps(message, indent = 4)


@app.route("/health-check", methods = ["GET"])
def health_check():
    message = "health check"
    channel_health_check.basic_publish(
        exchange= "", 
        routing_key="health_check", 
        body=message,
        properties=pika.BasicProperties(
                            delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE
                        )
        )
    return "Health check"

@app.route("/insert-record/<srn>/<name>/<section>", methods=["POST"])
def insert_record(srn, name, section):
    message = json.dumps({"name": name, "srn": srn, "section": section}, indent=4)
    print("{name:Vanshika,srn:PES1UG20CS698,section:L}")
    channel_insertion.basic_publish(
        exchange="",
        routing_key="insert_record",
        body=message.encode(),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        )
    )
    return "Insert Record"
        

@app.route("/delete-record/<srn>", methods=["GET"])
def delete_record(srn):
    message = json.dumps({"srn": srn})

    channel_deletion.basic_publish(
        exchange="", 
        routing_key="delete_record", 
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        )
    )
    return "Delete record"


@app.route("/read-database", methods=["GET"])
def read_records():
    print("{name:Vanshika,srn:PES1UG20CS698,section:L}")
    channel_read.basic_publish(
        exchange="", 
        routing_key="read_database", 
        body="",
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        )

    )
    return "Read database"
    


if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")



# based on route hit the required queue


# print("[x] Sent 'Hello world!'")

# connection.close()