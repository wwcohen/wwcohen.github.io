import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# --- 1. Define Sample Data ---
# x represents 'number of strokes'
x = np.arange(1, 26)

# y_mean represents the central line (mean score)
y_mountain_mean = 5.5 - 0.2 * x + np.sin(x/3) * 0.5
y_book_mean = 3.5 * np.exp(-(x - 8)**2 / (2 * 5**2)) + 0.5 * x / 10
y_whale_mean = 5.0 - 3.0 * np.exp(-x / 5)

# For a true Seaborn lineplot, we need the *raw data* or a consistent
# measure of dispersion (like standard error/SD) across multiple "trials" 
# at each x-point. Since you provided mean and SD, we'll simulate the raw data.
N_trials = 30  # Number of simulated observations per x-point

# Function to simulate N_trials data points based on mean (y_m) and SD (y_sd)
def simulate_data(x_arr, y_m, y_sd, category_name):
    data = []
    for i, x_val in enumerate(x_arr):
        # Generate N_trials points normally distributed around the mean with the given SD
        # We cap the data at the maximum length of the x array, matching the Matplotlib example
        if i < len(y_m):
            simulated_scores = np.random.normal(loc=y_m[i], scale=y_sd[i], size=N_trials)
            # Ensure scores are non-negative for realism, though not strictly necessary
            simulated_scores[simulated_scores < 0] = 0.01 
            
            for score in simulated_scores:
                data.append({
                    'number_of_strokes': x_val, 
                    'score': score, 
                    'category': category_name
                })
    return data

# Standard Deviations (same as in the Matplotlib example)
sd_mountain = 0.5 + 0.05 * x
sd_book = 0.5 + np.cos(x/5) * 0.3
sd_whale = 0.3 + 0.1 * np.random.rand(len(x))

# Truncate lines 1 and 2 SD arrays to match the Matplotlib example
sd_mountain = sd_mountain[:12]
sd_book = sd_book[:25]


# Simulate and combine the data (Note: we use the truncated x and y arrays here)
data_mountain = simulate_data(x[:12], y_mountain_mean[:12], sd_mountain, 'mountain')
data_book = simulate_data(x[:25], y_book_mean[:25], sd_book[:25], 'book')
data_whale = simulate_data(x, y_whale_mean, sd_whale, 'whale')

# Create the long-form DataFrame
df = pd.DataFrame(data_mountain + data_book + data_whale)


# --- 2. Create the Plot using Seaborn ---
plt.figure(figsize=(10, 6))

# The magic of Seaborn: one function call plots all lines, calculates the mean, 
# and computes the standard error (or confidence interval) for the shaded area.
# The `errorbar` parameter is key to defining the shaded region.
sns.lineplot(
    data=df, 
    x='number_of_strokes', 
    y='score', 
    hue='category',
    errorbar='sd', # Crucial: This tells Seaborn to use the Standard Deviation (SD) for the band
    linewidth=2
)

# --- 3. Customize and Style ---
plt.xlabel('number of strokes', fontsize=12)
plt.ylabel('score', fontsize=12)
plt.ylim(-0.5, 7.5) # Set Y limits to match the original image
# Seaborn automatically adds the legend and uses a clean, modern style.

plt.show()
