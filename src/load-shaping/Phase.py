class Phase:
    def __init__(self, start_time, duration, user_start, user_end, spawn_rate):
        self.start_time = start_time
        self.duration = duration
        self.user_start = user_start
        self.user_end = user_end
        self.spawn_rate = spawn_rate

    def user_count_at(self, t):
        if t < self.start_time or t > self.start_time + self.duration:
            return None
        if self.duration == 0:
            return self.user_end
        # Linear interpolation
        progress = (t - self.start_time) / self.duration
        return int(self.user_start + (self.user_end - self.user_start) * progress)
