import matplotlib.pyplot as plt
import numpy as np

# 1. Setup Data
# 'lots' of unique x values (e.g., 20 categories)
categories = [f"Item_{i}" for i in range(20)]
y_values_1 = np.random.randint(10, 50, size=20)
y_values_2 = np.random.randint(10, 50, size=20)

# 2. Define Coordinate System
# Create an array of indices: [0, 1, 2, ... , N-1]
x_indices = np.arange(len(categories))
width = 0.35  # Width of a single bar

# 3. Create the Figure
# Increase 'width' in figsize to accommodate many x-values
fig, ax = plt.subplots(figsize=(15, 6))

# 4. Plotting the Rectangles (The Math in action)
# We pass the calculated x-coordinates for each set
rects1 = ax.bar(x_indices - width/2, y_values_1, width, label='Group A', color='#4e79a7')
rects2 = ax.bar(x_indices + width/2, y_values_2, width, label='Group B', color='#f28e2b')

# 5. Low-Level Axis Formatting
ax.set_ylabel('Scores')
ax.set_title('Grouped Bar Chart with Dense X-Axis')

# Set the ticks exactly at the integer indices [0, 1, 2...]
ax.set_xticks(x_indices)

# Map the string labels to those integer indices
ax.set_xticklabels(categories)

# 6. Critical Step for "Lots of Values"
# Rotate labels 45 or 90 degrees to prevent overlap
plt.xticks(rotation=45, ha='right')

ax.legend()

# Layout adjustment to ensure rotated labels aren't cut off
plt.tight_layout()

plt.show()