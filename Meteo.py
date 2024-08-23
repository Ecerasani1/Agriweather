
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import tkinter as tk
from tkinter import ttk 

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 41.5864,
	"longitude": 12.9707,
	"current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m"],
	"minutely_15": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m"],
	"hourly": ["temperature_2m", "dew_point_2m", "evapotranspiration", "wind_speed_10m", "wind_direction_10m"],
	"daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "precipitation_probability_max", "wind_speed_10m_max", "wind_direction_10m_dominant"],
	"timezone": "auto",
	"past_days": 14,
	"forecast_days": 1
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = round(current.Variables(0).Value(), 1)
current_relative_humidity_2m = current.Variables(1).Value()
current_wind_speed_10m = round(current.Variables(2).Value(),1)
current_wind_direction_10m = current.Variables(3).Value()

print(f"Current time {current.Time()}")
print(f"Current temperature_2m {current_temperature_2m}")
print(f"Current relative_humidity_2m {current_relative_humidity_2m}")
print(f"Current wind_speed_10m {current_wind_speed_10m}")
print(f"Current wind_direction_10m {current_wind_direction_10m}")

# Process minutely_15 data. The order of variables needs to be the same as requested.
minutely_15 = response.Minutely15()
minutely_15_temperature_2m = minutely_15.Variables(0).ValuesAsNumpy()
minutely_15_relative_humidity_2m = minutely_15.Variables(1).ValuesAsNumpy()
minutely_15_wind_speed_10m = minutely_15.Variables(2).ValuesAsNumpy()
minutely_15_wind_direction_10m = minutely_15.Variables(3).ValuesAsNumpy()

minutely_15_data = {"date": pd.date_range(
	start = pd.to_datetime(minutely_15.Time(), unit = "s", utc = True),
	end = pd.to_datetime(minutely_15.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = minutely_15.Interval()),
	inclusive = "left"
)}
minutely_15_data["temperature_2m"] = minutely_15_temperature_2m
minutely_15_data["relative_humidity_2m"] = minutely_15_relative_humidity_2m
minutely_15_data["wind_speed_10m"] = minutely_15_wind_speed_10m
minutely_15_data["wind_direction_10m"] = minutely_15_wind_direction_10m

minutely_15_dataframe = pd.DataFrame(data = minutely_15_data)
print(minutely_15_dataframe)

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_dew_point_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_evapotranspiration = hourly.Variables(2).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()
hourly_wind_direction_10m = hourly.Variables(4).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["dew_point_2m"] = hourly_dew_point_2m
hourly_data["evapotranspiration"] = hourly_evapotranspiration
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["wind_direction_10m"] = hourly_wind_direction_10m

hourly_dataframe = pd.DataFrame(data = hourly_data)
print(hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(2).ValuesAsNumpy()
daily_precipitation_probability_max = daily.Variables(3).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(4).ValuesAsNumpy()
daily_wind_direction_10m_dominant = daily.Variables(5).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}
daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["precipitation_sum"] = daily_precipitation_sum
daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant

daily_dataframe = pd.DataFrame(data = daily_data)
print(daily_dataframe)



try:
     from ctypes import windll
     windll.shcore.SetProcessDpiAwareness(1)
except:
     pass



def Calcolo_resa(*args):
     try:
          olive = float(olive_input.get())
          olio = float(olio_input.get())
          resa = round(((olio/olive)*100),2)
          resa_input.set(f"La resa per quintale è {resa}")
     except ValueError:
          pass

root=tk.Tk()
root.title("Agriweather")


main_frame = ttk.Frame(root)
main_frame.grid(column=0, row=0, padx=10, pady=10)

dati_meteo = ttk.Frame(main_frame)
dati_meteo.grid(column=0, row=0)

temperatura_var = tk.StringVar()
temperatura_var.set(f"Temperatura corrente {current_temperature_2m}°C")
temperatura_label = ttk.Label(dati_meteo, textvariable=temperatura_var)
temperatura_label.grid(column=0, row=0, sticky="w")

umidità_var = tk.StringVar()
umidità_var.set(f"Umidità relativa {current_relative_humidity_2m}%")
umidità_label = ttk.Label(dati_meteo, textvariable=umidità_var)
umidità_label.grid(column=0, row=1,sticky="w")

velocità_vento_var = tk.StringVar()
velocità_vento_var.set(f"Velocità del vento {current_wind_speed_10m} Km/h")
velocità_vento_label = ttk.Label(dati_meteo, textvariable=velocità_vento_var)
velocità_vento_label.grid(column=0, row=3,sticky="w")

separator = ttk.Separator(main_frame, orient='vertical')
separator.grid(column=1, row=0, sticky='ns', padx=10)

dati_produzione = ttk.Frame(main_frame)
dati_produzione.grid(column=3, row=0)

olive_input =tk.StringVar()
olio_input = tk.StringVar()
resa_input = tk.StringVar()
oliva_label = ttk.Label(dati_produzione, text="Inserire quantità olive raccolte in kg:")
oliva_input =ttk.Entry(dati_produzione, textvariable=olive_input)
olio_label = ttk.Label(dati_produzione, text="Inserire quantità olio in kg:")
olio_input =ttk.Entry(dati_produzione, textvariable=olio_input)
resa_display = ttk.Label(dati_produzione, textvariable= resa_input)
resa_button = ttk.Button(dati_produzione, text="Calcola", command= Calcolo_resa)
oliva_label.grid(column=0, row=0, padx=5, pady=5, sticky="w")
olio_label.grid(column=0, row=1, padx=5, pady=5, sticky="w")
oliva_input.grid(column=1, row=0, padx=5, pady=5)
olio_input.grid(column=1, row=1, padx=5, pady=5)
resa_display.grid(column=1, row=2, padx=5, pady=5,sticky="w")
resa_button.grid(column=0, row=2, padx=5, pady=5,sticky="w")

     


root.mainloop()

