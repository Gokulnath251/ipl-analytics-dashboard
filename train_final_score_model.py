import pandas as pd
import numpy as np

deliveries = pd.read_csv("Ball_By_Ball_Match_Data.csv")

deliveries['TotalRun'] = pd.to_numeric(deliveries['TotalRun'], errors='coerce')
deliveries['IsWicketDelivery'] = pd.to_numeric(deliveries['IsWicketDelivery'], errors='coerce')

# cumulative score
deliveries['current_score'] = deliveries.groupby(['ID','Innings'])['TotalRun'].cumsum()

# wickets fallen
deliveries['wickets'] = deliveries.groupby(['ID','Innings'])['IsWicketDelivery'].cumsum()

# balls bowled
deliveries['ball_number'] = deliveries.groupby(['ID','Innings']).cumcount() + 1

deliveries['overs'] = deliveries['ball_number'] / 6

# final score
final_score = deliveries.groupby(['ID','Innings'])['TotalRun'].sum().reset_index()
final_score.columns = ['ID','Innings','final_score']

deliveries = deliveries.merge(final_score, on=['ID','Innings'])

# runs in last 30 balls (5 overs)
deliveries['runs_last_30'] = (
    deliveries.groupby(['ID','Innings'])['TotalRun']
    .transform(lambda x: x.rolling(30, min_periods=1).sum())
)

# wickets in last 30 balls
deliveries['wkts_last_30'] = (
    deliveries.groupby(['ID','Innings'])['IsWicketDelivery']
    .transform(lambda x: x.rolling(30, min_periods=1).sum())
)

data = deliveries[['current_score','overs','wickets','runs_last_30','wkts_last_30','final_score']]

data = data.dropna()

data.to_csv("final_score_training_data.csv", index=False)

print("Training dataset created!")


