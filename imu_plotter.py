import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Read the log file into a DataFrame with explicit datetime format
log_file = 'imu_log.txt'
df = pd.read_csv(log_file, sep=':::', header=None, engine='python')

# Extract datetime and data columns
df.columns = ['datetime', 'data']
df[['Acceleration', 'Angular_Velocity']] = df['data'].str.extract(r'IMU Acceleration: \[(.*?)\], IMU Angular Velocity: \[(.*?)\]')

# Convert data columns to numeric
df['Acceleration'] = df['Acceleration'].apply(lambda x: [float(i) for i in x.split()])
df['Angular_Velocity'] = df['Angular_Velocity'].apply(lambda x: [float(i) for i in x.split()])

# Calculate time index in seconds since the beginning of the flight (0.2 seconds apart)
time_delta = 0.2  # Time delta between data points in seconds
df['time_index'] = df.index * time_delta

# Plotting
plt.figure(figsize=(10, 6))
for axis in ['x', 'y', 'z']:
    plt.plot(df['time_index'], df['Acceleration'].apply(lambda acc: acc['xyz'.index(axis)]), label=f'Acceleration {axis}')
    plt.plot(df['time_index'], df['Angular_Velocity'].apply(lambda av: av['xyz'.index(axis)]), label=f'Angular Velocity {axis}')
plt.xlabel('Time (seconds since start of flight)')
plt.ylabel('Value')
plt.legend()
plt.title('IMU Data Visualization')

# Set finer ticks on the x-axis
plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=20))

plt.grid(True)
plt.show()
