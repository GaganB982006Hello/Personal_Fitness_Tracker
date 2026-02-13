import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from data_processor import FitnessDataProcessor

# Set style for dark mode
plt.style.use('dark_background')
sns.set_palette("husl")

def generate_visuals():
    processor = FitnessDataProcessor()
    df = processor.load_and_merge()
    df_processed = processor.preprocess(df.copy())

    # Ensure output dir exists
    output_dir = os.path.join('static', 'images')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Generating Figure 8: Null values heatmap...")
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.isnull(), yticklabels=False, cbar=False, cmap='viridis')
    plt.title('Null Values Heatmap')
    plt.savefig(os.path.join(output_dir, 'null_values.png'))
    plt.close()

    print("Generating Figure 9: Correlation Heatmap...")
    plt.figure(figsize=(12, 10))
    # Drop categorical or non-numeric if still present
    numeric_df = df_processed.select_dtypes(include=['float64', 'int64'])
    correlation = numeric_df.corr()
    sns.heatmap(correlation, cbar=True, square=True, fmt='.1f', annot=True, annot_kws={'size': 8}, cmap='Blues')
    plt.title('Correlation Heatmap')
    plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
    plt.close()

    print("Generating Figure 10: Outlier Boxplot...")
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df[['Age', 'Height', 'Weight', 'Duration', 'Heart_Rate', 'Body_Temp']])
    plt.title('Outlier Detection (Boxplot)')
    plt.savefig(os.path.join(output_dir, 'outliers_boxplot.png'))
    plt.close()

    print("Visuals generated successfully in static/images/")

if __name__ == "__main__":
    generate_visuals()
