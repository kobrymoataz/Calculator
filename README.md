# Python Kafka ZeroC Ice Calculator

A distributed calculator service implemented using ZeroC Ice for RMI and Apache Kafka for operation serialization. The service supports basic arithmetic operations (addition, subtraction, multiplication, and division) with proper error handling.

## Prerequisites

- Python 3.10 or higher
- Java Runtime Environment (JRE) for Kafka
- Apache Kafka
- ZeroC Ice

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment (recommended):
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Kafka Setup

1. Ensure Kafka and ZooKeeper are running on your system.

2. Create the required Kafka topics:
```bash
# Create calculator-requests topic
kafka-topics.sh --create --bootstrap-server localhost:9092 --topic calculator-requests --partitions 1 --replication-factor 1

# Create calculator-responses topic
kafka-topics.sh --create --bootstrap-server localhost:9092 --topic calculator-responses --partitions 1 --replication-factor 1
```

## Configuration

Create a `config.json` file in the project root with the following structure:
```json
{
    "kafka": {
        "bootstrap_servers": "localhost:9092",
        "request_topic": "calculator-requests",
        "response_topic": "calculator-responses",
        "consumer_group": "calculator-group",
        "auto_offset_reset": "earliest",
        "enable_auto_commit": true
    },
    "ice": {
        "identity": "CalculatorService",
        "endpoint": "default -p 10000",
        "adapter_name": "CalculatorAdapter"
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}
```

## Running the Project

### 1. Start the Ice Calculator Server

In one terminal:
```bash
python server.py
```

The server will start and listen for connections on port 10000.

### 2. Start the Kafka Consumer

In another terminal:
```bash
python kafka_handler/consumer.py
```

The consumer will start processing requests from the Kafka topic.

### 3. Run the Tests

In a third terminal:
```bash
python test_calculator.py
```

**Important**: Make sure both the Ice server and Kafka consumer are running before executing the tests.

## Test Cases

The test suite includes the following test cases:
- Basic arithmetic operations (addition, subtraction, multiplication, division)
- Division by zero error handling
- Invalid operation handling
- Malformed request handling

## Error Handling

The service handles various error cases:
- Division by zero: Returns "division by zero" error
- Invalid operations: Returns "Invalid operation" error
- Malformed requests: Returns "format error"
- Unknown calculation errors: Returns "Unknown calculation error"

## Project Structure

```
.
├── calculator/
│   ├── calculator_impl.py    # Ice calculator implementation
│   └── calculator_ice.py     # Generated Ice code
├── kafka_handler/
│   ├── consumer.py          # Kafka consumer implementation
│   ├── producer.py          # Kafka producer implementation
│   └── models.py            # Request/Response models
├── server.py                # Ice server entry point
├── test_calculator.py       # Test suite
├── config.json             # Configuration file
└── requirements.txt        # Project dependencies
```
