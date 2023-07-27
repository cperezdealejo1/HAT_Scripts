import csv
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from enviroplus import gas, noise
from smbus2 import SMBus
from bme280 import BME280
try:
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559
import logging

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

bus = SMBus(1)
bme280_sensor = BME280(i2c_dev=bus)

file_path = "sensor_data.csv"
total_duration_hours = 3
measurement_interval_minutes = 15

# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp

# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
factor = 1

while total_duration_hours > 0:
    start_time = time.time()
    end_time = start_time + measurement_interval_minutes * 60

    cpu_temps = [get_cpu_temperature()] * 5

    with open(file_path, "a", newline="") as file:
        writer = csv.writer(file)

        while time.time() < end_time:
            try:
                # Read light levels in lux
                lux = ltr559.get_lux()

                # Read weather data
                raw_temp = bme280_sensor.get_temperature()

                # Get CPU temperature for compensation
                cpu_temperature = get_cpu_temperature()

                # Smooth out with some averaging to decrease jitter
                cpu_temps = cpu_temps[1:] + [cpu_temperature]
                avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))

                # Compensate temperature
                comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)

                # Read pressure and humidity
                pressure = round(bme280_sensor.get_pressure(), 2)
                humidity = round(bme280_sensor.get_humidity(), 2)

                # Get current timestamp
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                # Write data to file
                writer.writerow([timestamp, lux, comp_temp, pressure, humidity, cpu_temperature])

                print(f"Light level: {lux} lux, Compensated Temperature: {comp_temp}°C, Pressure: {pressure} hPa, Humidity: {humidity}%, CPU Temperature: {cpu_temperature}°C")
                time.sleep(1)  # Wait for 1 second
            except KeyboardInterrupt:
                break

    with open(file_path, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([])  # Add an empty row between data blocks

    elapsed_time = time.time() - start_time
    remaining_time = max(0, (measurement_interval_minutes * 60) - elapsed_time)
    if remaining_time > 0:
        print(f"Waiting for {remaining_time} seconds until the next measurement...")
        time.sleep(remaining_time)

    total_duration_hours -= measurement_interval_minutes / 60

# Read data from the CSV file
df = pd.read_csv(file_path, parse_dates=[0])  # Assuming the timestamp is in the first column

# Plotting the graphs
fig, axs = plt.subplots(3, 1, figsize=(10, 12))
axs[0].plot(df.iloc[:, 0], df.iloc[:, 1])
axs[0].set_title('Light Level')
axs[0].set_ylabel('Lux')
axs[0].xaxis.set_major_locator(mdates.HourLocator())
axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

axs[1].plot(df.iloc[:, 0], df.iloc[:, 2])
axs[1].set_title('Temperature')
axs[1].set_ylabel('°C')
axs[1].xaxis.set_major_locator(mdates.HourLocator())
axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

axs[2].plot(df.iloc[:, 0], df.iloc[:, 4])
axs[2].set_title('Humidity')
axs[2].set_ylabel('%')
axs[2].set_xlabel('Time')
axs[2].xaxis.set_major_locator(mdates.HourLocator())
axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

plt.tight_layout()

# Save the figure
plt.savefig("sensor_data_plot.png")

# Show the plot
plt.show()
