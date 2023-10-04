import pandas as pd

# Load data (consider using a smaller chunk if the dataset is extremely large)
df = pd.read_csv("C:/Users/MMallon_DT/Downloads/2023q2/num.txt", delimiter='\t', nrows=100)  # Load only the first 100 rows

# To view a few rows of the dataframe
print(df.head())  # Display the first 5 rows
print(df.tail())  # Display the last 5 rows

# Describe data
print(df.describe())

# Info about data
print(df.info())
