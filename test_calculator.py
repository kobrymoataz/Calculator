from kafka import KafkaProducer, KafkaConsumer
import json
import time
import unittest
from typing import Dict, Any, Optional
import logging

class TestCalculator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize Kafka producer
        cls.producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Initialize Kafka consumer
        cls.consumer = KafkaConsumer(
            'calculator-responses',
            bootstrap_servers='localhost:9092',
            group_id='test-group',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def send_request_and_wait_for_response(self, request: Dict[str, Any], timeout: int = 5) -> Optional[Dict[str, Any]]:
        """Send a request and wait for the corresponding response."""
        request_id = request['id']
        print(f"\nSending request: {request}")
        
        # Send request
        self.producer.send('calculator-requests', value=request)
        self.producer.flush()
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < timeout:
            for message in self.consumer:
                response = message.value
                if response['id'] == request_id:
                    print(f"Received response: {response}")
                    return response
            time.sleep(0.1)
        
        self.fail(f"Timeout waiting for response to request {request_id}")

    def test_addition(self):
        request = {
            "id": "test_sum",
            "operation": "sum",
            "args": {
                "op1": 5.0,
                "op2": 10.4
            }
        }
        response = self.send_request_and_wait_for_response(request)
        self.assertTrue(response['status'])
        self.assertEqual(response['result'], 15.4)

    def test_subtraction(self):
        request = {
            "id": "test_sub",
            "operation": "sub",
            "args": {
                "op1": 10.0,
                "op2": 4.5
            }
        }
        response = self.send_request_and_wait_for_response(request)
        self.assertTrue(response['status'])
        self.assertEqual(response['result'], 5.5)

    def test_multiplication(self):
        request = {
            "id": "test_mult",
            "operation": "mult",
            "args": {
                "op1": 2.5,
                "op2": 3.0
            }
        }
        response = self.send_request_and_wait_for_response(request)
        self.assertTrue(response['status'])
        self.assertEqual(response['result'], 7.5)

    def test_division(self):
        request = {
            "id": "test_div",
            "operation": "div",
            "args": {
                "op1": 10.0,
                "op2": 2.0
            }
        }
        response = self.send_request_and_wait_for_response(request)
        self.assertTrue(response['status'])
        self.assertEqual(response['result'], 5.0)

    def test_division_by_zero(self):
        request = {
            "id": "test_div_zero",
            "operation": "div",
            "args": {
                "op1": 10.0,
                "op2": 0.0
            }
        }
        response = self.send_request_and_wait_for_response(request)
        self.assertFalse(response['status'])
        self.assertIn('error', response)
        self.assertIsNone(response.get('result'))

    def test_invalid_operation(self):
        request = {
            "id": "test_invalid_op",
            "operation": "invalid_op",
            "args": {
                "op1": 10.0,
                "op2": 2.0
            }
        }
        response = self.send_request_and_wait_for_response(request)
        self.assertFalse(response['status'])
        self.assertIn('error', response)
        self.assertIsNone(response.get('result'))

    def test_malformed_request(self):
        request = {
            "id": "test_malformed",
            "operation": "sum",
            "args": {
                "op1": "not_a_number",  # Invalid type
                "op2": 2.0
            }
        }
        response = self.send_request_and_wait_for_response(request)
        self.assertFalse(response['status'])
        self.assertIn('error', response)
        self.assertIsNone(response.get('result'))

    @classmethod
    def tearDownClass(cls):
        if cls.producer:
            cls.producer.close()
        if cls.consumer:
            cls.consumer.close()

if __name__ == '__main__':
    unittest.main() 