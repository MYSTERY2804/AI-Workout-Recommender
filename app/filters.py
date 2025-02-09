class WorkoutFilters:
    def apply_filters(self, df, body_part=None, difficulty=None, equipment=None, workout_type=None):
        if body_part:
            df = df[df["BodyPart"] == body_part]
        if difficulty:
            df = df[df["Level"] == difficulty]
        if equipment:
            df = df[df["Equipment"] == equipment]
        if workout_type:
            df = df[df["Type"] == workout_type]
        return df
