from Phase import Phase


class LoadProfileFactory:
    def __init__(self):
        self.phases = []
        self.current_time = 0

    def spike(self, users):
        self.phases.append(Phase(self.current_time, 0.1, users, users, users))
        self.current_time += 0.1
        return self

    def ramp_up(self, to_users, duration):
        from_users = self.phases[-1].user_end if self.phases else 0
        self.phases.append(Phase(self.current_time, duration, from_users, to_users, (to_users - from_users) / duration))
        self.current_time += duration
        return self

    def steady_users(self, users, duration):
        self.phases.append(Phase(self.current_time, duration, users, users, 1))
        self.current_time += duration
        return self

    def stress_ramp(self, from_users, to_users, duration):
        self.phases.append(Phase(self.current_time, duration, from_users, to_users, (to_users - from_users) / duration))
        self.current_time += duration
        return self

    def build(self):
        return self.phases
