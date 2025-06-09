from kafka import KafkaProducer, KafkaConsumer
import json
import sys
import os
import Ice
import traceback
import time
from typing import Dict, Any, Optional
import logging
from kafka_handler.models import CalculatorRequest, CalculatorResponse

# Load Ice slice files
SLICE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'calculator.ice')
Ice.loadSlice('', ['-I' + Ice.getSliceDir(), SLICE_PATH])
import Calculator

class ResponseProducer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.producer = None
        self.initialize_producer()

    def initialize_producer(self):
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                print(f"Attempting to initialize producer (attempt {attempt + 1}/{max_retries})...")
                self.producer = KafkaProducer(
                    bootstrap_servers=self.config['kafka']['bootstrap_servers'],
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                print("Producer initialized successfully")
                return
            except Exception as e:
                print(f"Error initializing producer (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise

    def send_response(self, response: CalculatorResponse):
        if self.producer:
            try:
                # Convert response to a simple dictionary
                response_data = {
                    "id": str(response.id),
                    "status": bool(response.status)
                }
                
                # Only add result if status is True
                if response.status:
                    response_data["result"] = float(response.result)
                
                # Only add error if status is False
                if not response.status:
                    response_data["error"] = str(response.error)
                
                print(f"Sending response: {response_data}")  # Debug print
                self.producer.send(
                    self.config['kafka']['response_topic'],
                    value=response_data
                )
                self.producer.flush()
            except Exception as e:
                print(f"Error sending response: {str(e)}")
                print(f"Response object: {response}")
                raise

class CalculatorConsumer:
    def __init__(self, config: Dict[str, Any], calculator_proxy: Ice.ObjectPrx):
        self.config = config
        self.calculator_proxy = calculator_proxy
        self.consumer = None
        self.producer = ResponseProducer(config)
        self.initialize_consumer()

    def initialize_consumer(self):
        self.consumer = KafkaConsumer(
            self.config['kafka']['request_topic'],
            bootstrap_servers=self.config['kafka']['bootstrap_servers'],
            group_id=self.config['kafka']['consumer_group'],
            auto_offset_reset=self.config['kafka']['auto_offset_reset'],
            enable_auto_commit=self.config['kafka']['enable_auto_commit'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def process_request(self, request_data: Dict[str, Any]) -> CalculatorResponse:
        # First check if the request has the basic structure
        if not isinstance(request_data, dict) or 'id' not in request_data or 'operation' not in request_data or 'args' not in request_data:
            req_id = request_data.get('id', 'unknown')
            return CalculatorResponse(id=req_id, status=False, error="format error")

        # Check for invalid operation before validation
        if request_data['operation'] not in ["sum", "sub", "mult", "div"]:
            return CalculatorResponse(id=request_data['id'], status=False, error="Invalid operation")

        try:
            request = CalculatorRequest.model_validate(request_data)
        except Exception as e:
            # If validation fails after operation check, it's a format error
            req_id = request_data.get('id', 'unknown')
            return CalculatorResponse(id=req_id, status=False, error="format error")

        try:
            args = request.args

            # Call the calculator method
            if request.operation == "sum":
                result = self.calculator_proxy.sum(args.op1, args.op2)
            elif request.operation == "sub":
                result = self.calculator_proxy.sub(args.op1, args.op2)
            elif request.operation == "mult":
                result = self.calculator_proxy.mult(args.op1, args.op2)
            elif request.operation == "div":
                result = self.calculator_proxy.div(args.op1, args.op2)

            # Check for error (assume NaN result or error attribute)
            error_msg = None
            if hasattr(self.calculator_proxy, 'last_error') and self.calculator_proxy.last_error:
                error_msg = self.calculator_proxy.last_error
            elif isinstance(result, float) and (result != result):  # NaN check
                if request.operation == "div" and request.args.op2 == 0:
                    error_msg = "division by zero"
                else:
                    error_msg = "Unknown calculation error."

            if error_msg:
                return CalculatorResponse(id=request.id, status=False, error=error_msg)
            else:
                return CalculatorResponse(id=request.id, status=True, result=result)

        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error processing request: {error_msg}")
            logging.error(traceback.format_exc())
            return CalculatorResponse(id=request.id, status=False, error="format error")

    def run(self):
        print("Starting Kafka consumer...")
        try:
            for message in self.consumer:
                try:
                    response = self.process_request(message.value)
                    self.producer.send_response(response)
                except Exception as e:
                    logging.error(f"Error processing message: {str(e)}")
                    logging.error(traceback.format_exc())
        except KeyboardInterrupt:
            print("Shutting down consumer...")
        finally:
            self.cleanup()

    def cleanup(self):
        if self.consumer:
            self.consumer.close()
        if self.producer and self.producer.producer:
            self.producer.producer.close()

def main():
    try:
        # Load configuration
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Initialize Ice
        communicator = Ice.initialize()
        proxy = communicator.stringToProxy(
            f"{config['ice']['identity']}:{config['ice']['endpoint']}"
        )
        calculator = Calculator.ServicePrx.checkedCast(proxy)

        if not calculator:
            raise RuntimeError("Invalid proxy")

        # Start consumer
        consumer = CalculatorConsumer(config, calculator)
        consumer.run()

    except Exception as e:
        print(f"Error during initialization: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
    finally:
        if 'communicator' in locals():
            communicator.destroy()

if __name__ == "__main__":
    main()