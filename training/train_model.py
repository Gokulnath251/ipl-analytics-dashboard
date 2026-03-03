
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle

# ---------------------------------
# LOAD DATA
# ---------------------------------

matches = pd.read_csv("Match_Info.csv")
balls = pd.read_csv("Ball_By_Ball_Match_Data.csv")

# ---------------------------------
# FIRST INNINGS SCORE (TARGET)
# ---------------------------------

first_innings = balls[balls['Innings'] == 1]

first_innings_score = first_innings.groupby('ID')['TotalRun'].sum().reset_index()

first_innings_score.rename(columns={'TotalRun':'first_innings_score'}, inplace=True)

# ---------------------------------
# SECOND INNINGS DATA
# ---------------------------------

second_innings = balls[balls['Innings'] == 2]

# ---------------------------------
# MERGE TARGET
# ---------------------------------

second_innings = second_innings.merge(first_innings_score, on='ID')

# ---------------------------------
# CURRENT SCORE
# ---------------------------------

second_innings['current_score'] = second_innings.groupby('ID')['TotalRun'].cumsum()

# ---------------------------------
# WICKETS FALLEN
# ---------------------------------

second_innings['wickets'] = second_innings.groupby('ID')['IsWicketDelivery'].cumsum()

# ---------------------------------
# BALLS BOWLED
# ---------------------------------

second_innings['balls_bowled'] = second_innings['Overs']*6 + second_innings['BallNumber']

# ---------------------------------
# BALLS LEFT
# ---------------------------------

second_innings['balls_left'] = 120 - second_innings['balls_bowled']

# ---------------------------------
# WICKETS LEFT
# ---------------------------------

second_innings['wickets_left'] = 10 - second_innings['wickets']

# ---------------------------------
# RUNS LEFT
# ---------------------------------

second_innings['runs_left'] = second_innings['first_innings_score'] - second_innings['current_score'] + 1

# ---------------------------------
# CURRENT RUN RATE
# ---------------------------------

second_innings['crr'] = second_innings['current_score'] / (second_innings['balls_bowled']/6)

# ---------------------------------
# REQUIRED RUN RATE
# ---------------------------------

second_innings['rrr'] = second_innings['runs_left'] / (second_innings['balls_left']/6)

# ---------------------------------
# MERGE MATCH RESULT
# ---------------------------------

data = second_innings.merge(matches, left_on='ID', right_on='match_number')

# ---------------------------------
# RESULT COLUMN
# ---------------------------------

data['result'] = (data['BattingTeam'] == data['winner']).astype(int)

# ---------------------------------
# FINAL DATASET
# ---------------------------------

final_df = data[['runs_left','balls_left','wickets_left','crr','rrr','result']]

final_df = final_df[final_df['balls_left'] > 0]
final_df = final_df.dropna()

# ---------------------------------
# TRAIN TEST SPLIT
# ---------------------------------

X = final_df[['runs_left','balls_left','wickets_left','crr','rrr']]
y = final_df['result']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------------------------
# TRAIN MODEL
# ---------------------------------

model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

# ---------------------------------
# ACCURACY
# ---------------------------------

accuracy = model.score(X_test, y_test)

print("Model Accuracy:", accuracy)

# ---------------------------------
# SAVE MODEL
# ---------------------------------

pickle.dump(model, open("win_predictor.pkl", "wb"))

print("Model saved successfully!")
