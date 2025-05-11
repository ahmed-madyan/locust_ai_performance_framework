from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from loguru import logger
from ..config import get_settings
import subprocess
import json
import os
from datetime import datetime

app = FastAPI(title="Locust Performance Testing Framework")
settings = get_settings()

class TestConfig(BaseModel):
    """Test configuration model"""
    users: int = settings.LOCUST_USERS
    spawn_rate: int = settings.LOCUST_SPAWN_RATE
    run_time: str = settings.LOCUST_RUN_TIME
    host: str = settings.LOCUST_HOST
    locustfile: str
    tags: Optional[Dict[str, Any]] = None

@app.post("/run-test")
async def run_test(config: TestConfig):
    """Run a Locust test with the given configuration"""
    try:
        # Prepare command
        cmd = [
            "locust",
            "--host", config.host,
            "--users", str(config.users),
            "--spawn-rate", str(config.spawn_rate),
            "--run-time", config.run_time,
            "--headless",
            "-f", config.locustfile
        ]
        
        # Add tags if provided
        if config.tags:
            for key, value in config.tags.items():
                cmd.extend(["--tags", f"{key}={value}"])
        
        # Run test
        logger.info(f"Starting test with config: {config.dict()}")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Test failed: {stderr}")
            raise HTTPException(status_code=500, detail=f"Test failed: {stderr}")
        
        # Parse results
        results = {
            "timestamp": datetime.now().isoformat(),
            "config": config.dict(),
            "output": stdout
        }
        
        # Save results
        results_dir = "test_results"
        os.makedirs(results_dir, exist_ok=True)
        
        result_file = os.path.join(
            results_dir,
            f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(result_file, "w") as f:
            json.dump(results, f, indent=2)
        
        return results
    
    except Exception as e:
        logger.error(f"Error running test: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 