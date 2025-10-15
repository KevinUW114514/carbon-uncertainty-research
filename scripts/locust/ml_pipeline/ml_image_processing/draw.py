import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df = pd.read_csv("ml_image_processing_results_1_cores.csv")  # change to your actual file name

# Extract the columns
x = df["size"]
y = df["main_duration_ms"]

# Create a scatter plot
plt.scatter(x, y, alpha=0.6, label="Data points")

# Calculate and plot a trend line (linear regression)
z = np.polyfit(x, y, 1)  # 1 = linear
p = np.poly1d(z)
plt.plot(x, p(x), "r--", label=f"Trend line: y={z[0]:.2f}x+{z[1]:.2f}")

# Labels and title
plt.xlabel("Size")
plt.ylabel("Main Duration")
plt.title("Scatter Plot with Trend Line")
plt.legend()
plt.grid(True)

# Show the plot
plt.savefig("ml_image_processing_scatter_plot.png")
