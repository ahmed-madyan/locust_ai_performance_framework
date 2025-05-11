# Locust AI Performance Testing Framework

A robust and modular framework for performance testing using Locust, with support for metrics collection, test scheduling, and visualization.

## Features

- Scalable test scenario definitions
- Custom user behavior classes
- Dynamic parameterization
- Structured test result aggregation
- Comprehensive logging with Loguru
- Test scheduling support
- Optional InfluxDB and Grafana integration
- FastAPI backend for test management
- Docker support

## Project Structure

```
.
├── src/
│   ├── api/
│   │   └── app.py              # FastAPI application
│   ├── locust_tasks/
│   │   └── base.py            # Base Locust user class
│   ├── tests/
│   │   └── sample_test.py     # Sample test scenarios
│   ├── utils/
│   │   ├── logging.py         # Logging configuration
│   │   └── metrics.py         # Metrics collection
│   └── config.py              # Application settings
├── Dockerfile
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your settings

## Running Tests

### Using the API

1. Start the FastAPI server:
   ```bash
   uvicorn src.api.app:app --reload
   ```
2. Send a POST request to `/run-test` with your test configuration

### Using Locust Directly

1. Navigate to the test directory:
   ```bash
   cd src/tests
   ```
2. Run Locust:
   ```bash
   locust -f sample_test.py
   ```

## Docker Support

Build and run the container:

```bash
docker build -t locust-framework .
docker run -p 8000:8000 locust-framework
```

## Metrics Collection

The framework supports pushing metrics to InfluxDB for visualization in Grafana. Configure your InfluxDB connection in the `.env` file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 