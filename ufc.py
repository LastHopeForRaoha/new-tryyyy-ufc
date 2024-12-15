import pandas as pd

# Define file paths
fight_stats_path = "/workspaces/ufc-json-test/processed_fight_data.csv"
main_dataset_path = "/workspaces/ufc-json-test/full_dataset_with_all_metrics.csv"
output_path = "/workspaces/ufc-json-test/updated_full_dataset_with_metrics.csv"

# Load datasets
print("Loading datasets...")
main_df = pd.read_csv(main_dataset_path)
fight_stats_df = pd.read_csv(fight_stats_path)

# Preprocess fight_stats_df for merging
print("Preprocessing fight_stats dataset...")
# Extract Fighter_A and Fighter_B from FIGHTER A VS FIGHTER B
fight_stats_df['Fighter_A'] = fight_stats_df['FIGHTER A VS FIGHTER B'].str.split(' VS ').str[0]
fight_stats_df['Fighter_B'] = fight_stats_df['FIGHTER A VS FIGHTER B'].str.split(' VS ').str[1]

# Drop unnecessary columns
fight_stats_df = fight_stats_df.drop(columns=['FIGHTER A VS FIGHTER B'])

# Merge logic
print("Merging datasets...")
# Merge on Fighter names and additional criteria
merged_df = pd.merge(
    main_df, fight_stats_df,
    left_on=['Fighter_R', 'Fighter_B', 'Winner'],
    right_on=['Fighter_A', 'Fighter_B', 'OUTCOME (FIGHTER A/FIGHTER B)'],
    how='left'
)

# Drop redundant columns post-merge
merged_df = merged_df.drop(columns=['Fighter_A', 'Fighter_B', 'OUTCOME (FIGHTER A/FIGHTER B)'], errors='ignore')

# Fill Victory and Loss Details columns
print("Filling victory and loss details...")
def fill_victory_loss(row):
    if row['Winner'] == 'Red':
        row['R_method_of_win'] = row['METHOD']
        row['R_round_of_win'] = row['ROUND']
        row['B_method_of_loss'] = row['METHOD']
        row['B_round_of_loss'] = row['ROUND']
    elif row['Winner'] == 'Blue':
        row['B_method_of_win'] = row['METHOD']
        row['B_round_of_win'] = row['ROUND']
        row['R_method_of_loss'] = row['METHOD']
        row['R_round_of_loss'] = row['ROUND']
    return row

# Apply the function
victory_loss_columns = ['R_method_of_win', 'R_round_of_win', 'B_method_of_loss', 'B_round_of_loss',
                        'B_method_of_win', 'B_round_of_win', 'R_method_of_loss', 'R_round_of_loss']

for col in victory_loss_columns:
    merged_df[col] = None

merged_df = merged_df.apply(fill_victory_loss, axis=1)

# Drop METHOD and ROUND columns after use
merged_df = merged_df.drop(columns=['METHOD', 'ROUND'], errors='ignore')

# Save the final dataset
print("Saving the final merged dataset...")
merged_df.to_csv(output_path, index=False)
print(f"Data processing complete. File saved to: {output_path}")
