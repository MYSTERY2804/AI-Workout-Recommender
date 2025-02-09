import pandas as pd
from app.filters import WorkoutFilters

class WorkoutRecommender:
    def __init__(self):
        self.file_path = "data/megaGymDataset.csv"
        self.df = pd.read_csv(self.file_path)
        self.df = self.df.drop(columns=["Unnamed: 0", "RatingDesc"], errors='ignore')
        self.filters = WorkoutFilters()

    def get_recommendations(self, body_part=None, difficulty=None, equipment=None, workout_type=None):
        filtered_df = self.filters.apply_filters(self.df, body_part, difficulty, equipment, workout_type)
        return filtered_df[["Title", "Type", "BodyPart", "Equipment", "Level", "Desc"]].to_dict(orient="records")
