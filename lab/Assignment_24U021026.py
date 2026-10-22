import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler
from scipy import stats

# ------------------------------------------
# Part A:
df = pd.read_excel(r'C:\Users\Mayank Rana\Desktop\code\python-for-ai\lab\Employee salary prediction.xlsx',skiprows=2)

print("First 10 records:\n", df.head(10))
print("Last 10 records:\n", df.tail(10))

print("Number of rows:", df.shape[0])
print("Number of columns:", df.shape[1])

print("\nData Types:\n", df.dtypes)

print("\nStatistical Summary:\n", df.describe())

print("\nMissing Values:\n", df.isnull().sum())
print("Duplicate Records:", df.duplicated().sum())

# Identify numerical and categorical columns
num_cols = df.select_dtypes(include=['number']).columns.tolist()
cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
print("\nNumerical Columns:", num_cols)
print("Categorical Columns:", cat_cols)

# ==========================================
# Part B: Missing Value Handling
# ==========================================
# Step 1: Identify Missing Values
print("\nMissing values:\n", df.isnull().sum())

# Visualize missing values (Heatmap & Bar Chart)
sns.heatmap(df.isnull(), cmap='viridis', cbar=False)
plt.title("Missing Values Heatmap")
plt.show()

df.isnull().sum().plot(kind='bar')
plt.title("Missing Values Bar Chart")
plt.show()

# Step 2: Numerical Missing Value Imputation
# Creating copies to test methods
df_mean = df.copy()
df_median = df.copy()
df_knn = df.copy()

mean_imputer = SimpleImputer(strategy='mean')
df_mean[num_cols] = mean_imputer.fit_transform(df_mean[num_cols])

median_imputer = SimpleImputer(strategy='median')
df_median[num_cols] = median_imputer.fit_transform(df_median[num_cols])

knn_imputer = KNNImputer(n_neighbors=3)
df_knn[num_cols] = knn_imputer.fit_transform(df_knn[num_cols])

# Step 3: Categorical Missing Value Imputation
mode_imputer = SimpleImputer(strategy='most_frequent')
df_mean[cat_cols] = mode_imputer.fit_transform(df_mean[cat_cols])
df_median[cat_cols] = mode_imputer.fit_transform(df_median[cat_cols])
df_knn[cat_cols] = mode_imputer.fit_transform(df_knn[cat_cols])

# Step 4: Comparison (Textual answers usually go here, keeping it as code prints)
print("\nComparison Advantages/Disadvantages:")
print("Mean: Easy to use / Sensitive to outliers")
print("Median: Robust to outliers / Ignores feature relationships")
print("Mode: Best for categorical / Can skew data if one category dominates")
print("KNN: Highly accurate / Computationally heavy")

# Step 5: Statistical Analysis Comparison (Example on Salary)
print("\nOriginal Salary Stats:\n", df['Salary'].describe()[['mean', '50%', 'std']])
print("\nMean Imputed Salary Stats:\n", df_mean['Salary'].describe()[['mean', '50%', 'std']])

# Step 6: Visualization comparison
plt.hist([df['Salary'].dropna(), df_mean['Salary'], df_median['Salary'], df_knn['Salary']], 
         label=['Original', 'Mean', 'Median', 'KNN'])
plt.legend()
plt.title("Histogram Comparison")
plt.show()

plt.boxplot([df['Salary'].dropna(), df_mean['Salary'], df_median['Salary'], df_knn['Salary']], 
            labels=['Original', 'Mean', 'Median', 'KNN'])
plt.title("Boxplot Comparison")
plt.show()

# Setting df to the knn imputed version for the remaining tasks
df = df_knn.copy()

# ==========================================
# Part C: Duplicate Record Handling
# ==========================================
# Detect duplicate records
print("\nDuplicate records mask:\n", df.duplicated())

# Count duplicates
print("Number of duplicates:", df.duplicated().sum())

# Compare dataset size before and after removal
print("Size before removal:", df.shape)

# Remove duplicates
df = df.drop_duplicates()
print("Size after removal:", df.shape)


# ==========================================
# Part D: Handling Categorical Features
# ==========================================
print("\nNumber of features before encoding:", df.shape[1])

# 1. Label Encoding
le = LabelEncoder()
for col in ['Gender', 'Marital_Status', 'Overtime']:
    df[col] = le.fit_transform(df[col].astype(str))

# 2. One-Hot Encoding
df = pd.get_dummies(df, columns=['Education', 'Department', 'City', 'Work_Mode'])

# 3. Compare Encoding Methods
print("Label Encoding: Keeps feature count same / ML might assume numerical order.")
print("One-Hot Encoding: No artificial order / Increases feature count (dimensionality).")

# 4. Display
print("Number of features after encoding:", df.shape[1])


# ==========================================
# Part E: Outlier Detection and Handling
# ==========================================
# Method 1: Boxplot
df[['Age', 'Experience', 'Monthly_Hours', 'Salary']].boxplot()
plt.title("Boxplot for Outlier Detection")
plt.show()

# Method 2: IQR Method (Example using Salary)
Q1 = df['Salary'].quantile(0.25)
Q3 = df['Salary'].quantile(0.75)
IQR = Q3 - Q1
Lower_Bound = Q1 - 1.5 * IQR
Upper_Bound = Q3 + 1.5 * IQR
print(f"\nIQR Lower Bound: {Lower_Bound}, Upper Bound: {Upper_Bound}")

# Method 3: Z-Score Method
z_scores = stats.zscore(df['Salary'])

# Handle outliers
# Approach A: Capping
df_capped = df.copy()
df_capped['Salary'] = np.clip(df_capped['Salary'], Lower_Bound, Upper_Bound)

# Approach B: Removal
df_removed = df[(df['Salary'] >= Lower_Bound) & (df['Salary'] <= Upper_Bound)]

print("Size after capping:", df_capped.shape)
print("Size after removal:", df_removed.shape)
df = df_capped  # Using capped to avoid losing data


# ==========================================
# Part F: Feature Scaling
# ==========================================
cols_to_scale = ['Age', 'Experience', 'Monthly_Hours', 'Salary', 'Previous_Company']

# 1. Min-Max Scaling
min_max = MinMaxScaler()
df_minmax = df.copy()
df_minmax[cols_to_scale] = min_max.fit_transform(df_minmax[cols_to_scale])

# 2. Standardization
std_scaler = StandardScaler()
df_std = df.copy()
df_std[cols_to_scale] = std_scaler.fit_transform(df_std[cols_to_scale])

# Compare using visualization (Histogram and Boxplot)
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
axes[0].hist(df['Experience'])
axes[0].set_title('Original Experience')
axes[1].hist(df_minmax['Experience'])
axes[1].set_title('Min-Max Scaled')
axes[2].hist(df_std['Experience'])
axes[2].set_title('Standardized')
plt.show()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
axes[0].boxplot(df['Experience'])
axes[0].set_title('Original Experience Boxplot')
axes[1].boxplot(df_minmax['Experience'])
axes[1].set_title('Min-Max Scaled Boxplot')
axes[2].boxplot(df_std['Experience'])
axes[2].set_title('Standardized Boxplot')
plt.show()