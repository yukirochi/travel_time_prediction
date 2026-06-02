from snowflake_info import cur
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.metrics import mean_absolute_error
import pandas as pd
import matplotlib.pyplot as plt
df = cur.execute("SELECT * FROM training_data.staging_mart.mart_data").fetch_pandas_all()


x = df[['DAY_OF_WEEK', 'DEPARTURE_TIME']]

y = df['TRAVEL_TIME_IN_MINUTES']


X_train, X_test, Y_train, Y_test = train_test_split(x, y, test_size=0.2, random_state=42)


regressor = DecisionTreeRegressor(max_depth=4, random_state=42)

regressor.fit(X_train, Y_train)


predictions = regressor.predict(X_test)
error = mean_absolute_error(Y_test, predictions)
print(f"Mean Absolute Error: {error:.2f} minutes")

input_trip = pd.DataFrame({
    'DAY_OF_WEEK': [1],  # Monday
    'DEPARTURE_TIME': [2.51] 
})
 
predicted_time = regressor.predict(input_trip)
print(f"input_trip: {input_trip.to_dict(orient='records')[0]}")
print(f"Predicted Travel Time: {predicted_time[0]:.2f} minutes")