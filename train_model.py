import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import joblib

df=pd.read_csv('properties.csv')

print("Dataset loaded successfully!")
print(f"Shape: {df.shape}") # (rows, columns)


print(df.head()) 
print(df.tail())
print(df.info())
print(df.columns.tolist()) 

# Missing values per column
print("\nMissing values:")
print(df.isnull().sum())

print(df.describe()) # statistical summary of numerical columns
print("\nPrice range:")
print(f" Min: AED {df['price'].min():,.0f}")
print(f" Max: AED {df['price'].max():,.0f}") #35M apartment is an outlier - exeeds the mean by 10x
print(f" Median: AED {df['price'].median():,.0f}")
print(f" Mean: AED {df['price'].mean():,.0f}")

#⚠ Mean vs Median are very different — this means there are some ultra-luxury apartments (AED 45M!) pulling the average up. 
#These are called outliers.

# How many luxury outliers (over AED 10M)?
outliers = df[df['price'] > 10_000_000]
print(f"\nApartments over AED 10M: {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")

# How many unique neighborhoods?
print(f"Unique neighborhoods: {df['neighborhood'].nunique()}") #nunique()-how many different neighborhoods are there?
print(df['neighborhood'].value_counts().head(10)) # value_counts()-tallies the occurences ,default in sorted order(highest to lowest)

# What quality levels exist?
print(f"Quality values: {df['quality'].unique()}") #unique-gives the distinct values in the column in a list format
print(df['quality'].value_counts())

# Boolean amenities — % of apartments that have each
print("\nAmenity prevalence:")
bool_cols = df.select_dtypes(include='bool').columns
for col in bool_cols:
    pct = df[col].mean() * 100
    print(f" {col:<25} {pct:5.1f}% of apartments")

#----------------------------------------------------------------------
#Removing outliers

print(f"Rows before: {len(df)}") 
print(f"Price max before: AED{df['price'].max():,.0f}")

# Keep only apartments priced at or below AED 10 million
# df[condition] = "give me all rows where condition is True"
df = df[df['price'] <= 10_000_000]

print(f"Rows after: {len(df)}")
print(f"Price max after: AED {df['price'].max():,.0f}")
print(f"Removed: {1905 - len(df)} outlier rows")

# Drop useless columns
# axis=1 means "drop a column" (axis=0 would drop a row)
df = df.drop(columns=['id', 'price_per_sqft'])

print(f"Columns remaining: {len(df.columns)}")
print(df.columns.tolist()) 
#------------------------------------------------------------------
#Encoding 

quality_order = {'Low': 0, 'Medium': 1, 'High': 2, 'Ultra': 3}
# .map() swaps every text value with its number
df['quality_encoded'] = df['quality'].map(quality_order)
# Drop the original text column
df = df.drop(columns=['quality'])

# Verify it worked
print(df[['quality_encoded']].value_counts().sort_index())
print(f"Any NaN? {df['quality_encoded'].isnull().sum()}")

#one-hot encoding for neighborhood
print(f"Columns before encoding: {len(df.columns)}")

# get_dummies() creates one new column per neighborhood
# prefix='nbhd' → column names become: nbhd_Dubai Marina
# drop_first=True → avoids the "dummy variable trap" (explained below)
df = pd.get_dummies(df, columns=['neighborhood'],
                   prefix='nbhd', drop_first=True)

print(f"Columns after encoding: {len(df.columns)}")
nbhd_cols = [c for c in df.columns if c.startswith('nbhd_')]
print(f"Neighborhood columns: {len(nbhd_cols)} (one per area)")

print(f"Final shape: {df.shape}")
print(f"Any NaN left? {df.isnull().sum().sum()}")
print(f"Price range: AED {df['price'].min():,.0f} – AED {df['price'].max():,.0f}")
print("\n✓ Ready for modelling!")
#---------------------------------------------------------------------------
#Split data

# X = every column EXCEPT price (the inputs)
# y = just the price column (what we want to predict)
X = df.drop(columns=['price'])
y = df['price']

print(f"X shape: {X.shape}") 
print(f"y shape: {y.shape}")

# scikit-learn needs numbers, not True/False
# This converts: True→1, False→0
bool_cols = X.select_dtypes(include='bool').columns
X[bool_cols] = X[bool_cols].astype(int)

print("Data types in X:")
print(X.dtypes.value_counts())

# Split: 80% for training, 20% for testing
# random_state=42 → same shuffle every run (reproducible)
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2, # 20% goes to test
    random_state=42 # fixed shuffle seed
)

print(f"Training set: {X_train.shape[0]} apartments ← model SEES these")
print(f"Test set: {X_test.shape[0]} apartments ← model NEVER sees these")

model=LinearRegression()#blank training model
model.fit(X_train,y_train) #train the model on the training data

print("✓ Model trained!")
print(f" Weights learned: {len(model.coef_)}")
print(f" Bias learned: AED {model.intercept_:,.0f}")

y_pred = model.predict(X_test)
print("Sample predictions vs actual prices:")
print(f" {'Actual':<18} {'Predicted':<18} {'Difference'}")
for i in range(5):
    actual = y_test.iloc[i]
    predicted = y_pred[i]
    diff = predicted - actual
    sign = "+" if diff > 0 else ""
    print(f" AED {actual:>10,.0f} AED {predicted:>10,.0f} {sign}AED {diff:,.0f}")

# RMSE: average error in AED (same unit as price)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

# R²: % of price variation the model explains (0=useless, 1=perfect)
r2 = r2_score(y_test, y_pred)


print(f"RMSE: AED {rmse:,.0f}")
print(f"R²: {r2:.4f} ({r2*100:.1f}% of price variation explained)")
      
coef_df = pd.DataFrame({
    'feature': X.columns,
    'weight': model.coef_
})
coef_df['abs_weight'] = coef_df['weight'].abs()
coef_df = coef_df.sort_values('abs_weight', ascending=False)

print("Top 10 most influential features:")
for _, row in coef_df.head(10).iterrows():
    direction = "↑ raises" if row["weight"] > 0 else "↓ lowers"
    print(f" {row['feature']:<35} {direction} price by AED {abs(row['weight']):>10,.0f}")

print(f"RMSE: AED {rmse:,.0f} | R²: {r2:.4f}")
print("✓ Linear Regression complete!")

# n_estimators=100 → build 100 decision trees
# random_state=42 → reproducible results
# n_jobs=-1 → use all your CPU cores (trains faster)
rf_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

# Exact same pattern as LinearRegression — scikit-learn is consistent!
rf_model.fit(X_train, y_train)
print("✓ Random Forest trained!")
print(f" Trees built: {rf_model.n_estimators}")
print(f" Features used: {rf_model.n_features_in_}")

# Predict on the same 373 test apartments
rf_pred = rf_model.predict(X_test)

# Evaluate
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
rf_r2   = r2_score(y_test, rf_pred)

# Side-by-side comparison
print(f"R²: Linear={0.6453:.4f} → RF={rf_r2:.4f} (+{rf_r2-0.6453:.4f})")
print(f"RMSE: Linear=AED 708,412 → RF=AED {rf_rmse:,.0f} (AED {708412-rf_rmse:,.0f} better)")

# Row-by-row comparison: LR vs RF vs Actual
print(f"{'Actual':>14} {'Linear Reg':>14} {'RandomForest':>14} Winner")
print("-" * 65)
for i in range(6):
    actual = y_test.iloc[i]
    lr_p = y_pred[i] # from step 3b
    rf_p = rf_pred[i]
    lr_err = abs(lr_p - actual)
    rf_err = abs(rf_p - actual)
    winner = "RF ✓" if rf_err < lr_err else "LR ✓"
    print(f"AED {actual:>9,.0f} AED {lr_p:>9,.0f} AED {rf_p:>9,.0f} {winner}")

    # Feature importances — what RF actually learned matters
fi_df = pd.DataFrame({
    'feature': X.columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("Top 10 most important features (RF):")
for _, row in fi_df.head(10).iterrows():
    bar = "█" * int(row["importance"] * 100)
    print(f" {row['feature']:<30} {bar:<12} {row['importance']*100:5.1f}%")

# Save the trained RF model to a file
# Flask will load this — no need to retrain every time
joblib.dump(rf_model, 'dubai_model.pkl')

# Also save the column list — Flask needs the EXACT same column
# order as training, or predictions will be completely wrong
joblib.dump(X.columns.tolist(), 'model_columns.pkl')

print("✓ Model saved: dubai_model.pkl")
print("✓ Columns saved: model_columns.pkl")

