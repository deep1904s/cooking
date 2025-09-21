import pandas as pd

df = pd.read_csv("../data/foodcom-recipes-and-reviews/recipes.csv")
print(df.head())
print(df.columns)
print("Total recipes:", len(df))
