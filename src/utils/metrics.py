from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from loguru import logger
from typing import Dict, Any, Optional
from ..config import get_settings
import time

class MetricsCollector:
    """Collect and store metrics in InfluxDB"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.write_api = None
        self._setup_influxdb()
    
    def _setup_influxdb(self):
        """Setup InfluxDB connection if configured"""
        if all([
            self.settings.INFLUXDB_URL,
            self.settings.INFLUXDB_TOKEN,
            self.settings.INFLUXDB_ORG,
            self.settings.INFLUXDB_BUCKET
        ]):
            try:
                self.client = InfluxDBClient(
                    url=self.settings.INFLUXDB_URL,
                    token=self.settings.INFLUXDB_TOKEN,
                    org=self.settings.INFLUXDB_ORG
                )
                self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
                logger.info("InfluxDB connection established")
            except Exception as e:
                logger.error(f"Failed to connect to InfluxDB: {e}")
                self.client = None
                self.write_api = None
    
    def record_metric(self, 
                     measurement: str,
                     fields: Dict[str, Any],
                     tags: Optional[Dict[str, str]] = None,
                     timestamp: Optional[int] = None):
        """
        Record a metric in InfluxDB
        
        Args:
            measurement: Name of the measurement
            fields: Dictionary of field values
            tags: Optional dictionary of tags
            timestamp: Optional timestamp (defaults to current time)
        """
        if not self.write_api:
            return
        
        try:
            point = Point(measurement)
            
            # Add fields
            for key, value in fields.items():
                point = point.field(key, value)
            
            # Add tags
            if tags:
                for key, value in tags.items():
                    point = point.tag(key, value)
            
            # Add timestamp
            if timestamp is None:
                timestamp = int(time.time() * 1e9)  # Convert to nanoseconds
            point = point.time(timestamp)
            
            # Write to InfluxDB
            self.write_api.write(
                bucket=self.settings.INFLUXDB_BUCKET,
                record=point
            )
        except Exception as e:
            logger.error(f"Failed to write metric to InfluxDB: {e}")
    
    def close(self):
        """Close InfluxDB connection"""
        if self.client:
            self.client.close()
            logger.info("InfluxDB connection closed") 