from locust import LoadTestShape, HttpUser, task
from typing import Optional, Tuple
from LoadProfileFactory import LoadProfileFactory


class CustomLoadShape(LoadTestShape):
    """
    A custom load shape that implements a complex load pattern using multiple phases:
    - Initial spike
    - Ramp up
    - Steady state
    - Stress test
    """
    
    # Load test configuration constants
    INITIAL_SPIKE_USERS = 10
    RAMP_UP_USERS = 20
    RAMP_UP_DURATION = 10
    STEADY_USERS = 5
    STEADY_DURATION = 5
    STRESS_START_USERS = 5
    STRESS_END_USERS = 15
    STRESS_DURATION = 10

    def __init__(self) -> None:
        """Initialize the load shape with predefined phases."""
        super().__init__()
        self.phases = LoadProfileFactory() \
            .spike(self.INITIAL_SPIKE_USERS) \
            .ramp_up(self.RAMP_UP_USERS, self.RAMP_UP_DURATION) \
            .steady_users(self.STEADY_USERS, self.STEADY_DURATION) \
            .stress_ramp(self.STRESS_START_USERS, self.STRESS_END_USERS, self.STRESS_DURATION) \
            .build()

    def tick(self) -> Optional[Tuple[int, float]]:
        """
        Calculate the number of users and spawn rate for the current time.
        
        Returns:
            Optional[Tuple[int, float]]: A tuple of (user_count, spawn_rate) or None if no phase is active
        """
        run_time = self.get_run_time()

        for phase in self.phases:
            user_count = phase.user_count_at(run_time)
            if user_count is not None:
                return (user_count, phase.spawn_rate)

        return None


class MyUser(HttpUser):
    """
    A test user that simulates API calls to a dummy endpoint.
    """
    host = "https://httpbin.org"  # Dummy endpoint for testing
    wait_time = lambda self: 1

    @task
    def hit_dummy_api(self) -> None:
        """Make a GET request to the dummy API endpoint."""
        self.client.get("/get")  # /get is a simple echo endpoint
