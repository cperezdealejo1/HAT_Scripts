import csv
import time
import datetime

from grow.moisture import Moisture
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

try:
    m1 = Moisture(1)
    m2 = Moisture(2)
    m3 = Moisture(3)
except Exception as e:
    print("Error initializing moisture sensors:", e)
    exit(1)

# Data collection for 15 minutes, repeated for a total of three hours
total_duration = datetime.timedelta(hours=3)
collection_duration = datetime.timedelta(minutes=15)
end_time = datetime.datetime.now() + total_duration

data = []

try:
    while datetime.datetime.now() < end_time:
        start_time = datetime.datetime.now()
        current_data = []

        while datetime.datetime.now() < (start_time + collection_duration):
            try:
                # Get the current timestamp
                timestamp = datetime.datetime.now()

                # Read moisture data
                moisture1 = m1.moisture
                moisture2 = m2.moisture
                moisture3 = m3.moisture

                # Append data to the list
                current_data.append({
                    'Timestamp': timestamp,
                    'Moisture 1': moisture1,
                    'Moisture 2': moisture2,
                    'Moisture 3': moisture3
                })

                # Display current data
                print(f"Timestamp: {timestamp}, Moisture 1: {moisture1}, Moisture 2: {moisture2}, Moisture 3: {moisture3}")

                # Wait for 1 second before the next reading
                time.sleep(1)

            except Exception as e:
                print("Error reading moisture data:", e)

        # Append current data to the main data list
        data.extend(current_data)

        # Save current data to CSV file
        try:
            with open('moisture_data.csv', 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=current_data[0].keys())
                if file.tell() == 0:
                    writer.writeheader()
                writer.writerows(current_data)
        except Exception as e:
            print("Error saving data to CSV:", e)

except KeyboardInterrupt:
    print("Data collection interrupted by the user.")

# Read data from the CSV file
try:
    df = pd.read_csv('moisture_data.csv', parse_dates=['Timestamp'])
except Exception as e:
    print("Error reading data from CSV:", e)
    exit(1)

# Plotting the graphs
fig, axs = plt.subplots(3, 1, figsize=(10, 12))
axs[0].plot(df['Timestamp'], df['Moisture 1'])
axs[0].set_title('Moisture 1')
axs[0].set_ylabel('Moisture Level')
axs[0].xaxis.set_major_locator(mdates.HourLocator())
axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

axs[1].plot(df['Timestamp'], df['Moisture 2'])
axs[1].set_title('Moisture 2')
axs[1].set_ylabel('Moisture Level')
axs[1].xaxis.set_major_locator(mdates.HourLocator())
axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

axs[2].plot(df['Timestamp'], df['Moisture 3'])
axs[2].set_title('Moisture 3')
axs[2].set_ylabel('Moisture Level')
axs[2].set_xlabel('Time')
axs[2].xaxis.set_major_locator(mdates.HourLocator())
axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

plt.tight_layout()

# Show the plot and update it with new data in real-time
plt.ion()
plt.show()

# Continuously update the plot with new data
while True:
    # Read latest data from CSV file
    try:
        df = pd.read_csv('moisture_data.csv', parse_dates=['Timestamp'])
    except Exception as e:
        print("Error reading data from CSV:", e)
        exit(1)

    # Update the plot
    axs[0].cla()
    axs[0].plot(df['Timestamp'], df['Moisture 1'])
    axs[0].set_title('Moisture 1')
    axs[0].set_ylabel('Moisture Level')
    axs[0].xaxis.set_major_locator(mdates.HourLocator())
    axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

    axs[1].cla()
    axs[1].plot(df['Timestamp'], df['Moisture 2'])
    axs[1].set_title('Moisture 2')
    axs[1].set_ylabel('Moisture Level')
    axs[1].xaxis.set_major_locator(mdates.HourLocator())
    axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

    axs[2].cla()
    axs[2].plot(df['Timestamp'], df['Moisture 3'])
    axs[2].set_title('Moisture 3')
    axs[2].set_ylabel('Moisture Level')
    axs[2].set_xlabel('Time')
    axs[2].xaxis.set_major_locator(mdates.HourLocator())
    axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

    plt.tight_layout()
    plt.pause(1)
