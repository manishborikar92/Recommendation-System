import pandas as pd

# Define the required columns to keep
required_columns = [
    'product_id', 'product_name', 'category', 'discounted_price',
    'actual_price', 'discount_percentage', 'rating', 'rating_count',
    'about_product', 'img_link', 'product_features'
]

# Read the CSV file
df = pd.read_csv('data/processed/preprocessed_data.csv')  # Replace 'input.csv' with your actual file name

# Keep only the required columns
df_filtered = df[required_columns]

# # Remove rows with any missing values in the required columns
# df_cleaned = df_filtered.dropna(subset=required_columns)

# Save the cleaned data to a new CSV file
df_filtered.to_csv('data/processed/cleaned_data.csv', index=False)

print("Data preprocessing completed. Cleaned data saved to 'cleaned_data.csv'")