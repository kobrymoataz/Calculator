import json
from kafka import KafkaConsumer
from kafka_handler.producer import ResponseProducer
import Ice
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from calculator import calculator_ice
import Calculator

with open('config.json') as f:
    config = json.load(f)

producer = ResponseProducer(config)

consumer = KafkaConsumer(
    config['kafka']['request_topic'],
    bootstrap_servers=config['kafka']['bootstrap_servers'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='calculator-group'
)

with Ice.initialize(sys.argv) as communicator:
    base = communicator.stringToProxy("CalculatorService:default -p 10000")
    calculator = Calculator.ServicePrx.checkedCast(base)

    if not calculator:
        raise RuntimeError("Invalid proxy")

    print("Kafka consumer started...")
    for msg in consumer:
        data = msg.value
        response = {"id": data.get("id"), "status": False}
        try:
            op = data["operation"]
            op1 = data["args"]["op1"]
            op2 = data["args"]["op2"]

            if op == "sum":
                result = calculator.sum(op1, op2)
            elif op == "sub":
                result = calculator.sub(op1, op2)
            elif op == "mult":
                result = calculator.mult(op1, op2)
            elif op == "div":
                result = calculator.div(op1, op2)
            else:
                raise ValueError("operation not found")

            response.update({"status": True, "result": result})

        except ZeroDivisionError:
            response["error"] = "zero"
        except Exception as e:
            response["error"] = str(e)

        producer.send_response(response)