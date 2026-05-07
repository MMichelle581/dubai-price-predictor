#Removing outliers
print(f"Rows before: {len(df)}") 
print(f"Price max before: AED{df['price'].max():,.0f}")

# Keep only apartments priced at or below AED 10 million
# df[condition] = "give me all rows where condition is True"
df = df[df['price'] <= 10_000_000]

print(f"Rows after: {len(df)}")
print(f"Price max after: AED {df['price'].max():,.0f}")
print(f"Removed: {1905 - len(df)} outlier rows")