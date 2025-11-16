import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import configparser

# Location
latitude = 28.81
longitude = -81.71  # West is negative

# Config Info
config = configparser.ConfigParser()
config.read(r'D:\Program Files (x86)\PyCharm Projects\Plant-Freeze Alert\config.ini')

from_email = config['EMAIL']['from_email']
to_email = config['EMAIL']['from_email']
password = config['EMAIL']['password']

# Email Function
def send_email(message_body):
    msg = MIMEText(message_body)
    msg['Subject'] = 'Freeze Warning'
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
            print(f'Email sent: {message_body}')
    except Exception as e:
        print(f'Failed to send email: {e}')

# Getting metadata from weather.gov
url = f'https://api.weather.gov/points/{latitude},{longitude}'
response = requests.get(url)

if not response.ok:
    print(f'Error: {response.status_code}')
    exit()
data = response.json()
hourly_url = data['properties']['forecastHourly']
city = data['properties']['relativeLocation']['properties']['city']
state = data['properties']['relativeLocation']['properties']['state']
#------TESTING--------
#print(f'Location : {city}, {state}')
#print(hourly_url)

# Getting hourly data
hourly_response = requests.get(hourly_url)

if not hourly_response.ok:
    print(f'Error on hourly response: {hourly_response.status_code}')
    exit()

hourly_data = hourly_response.json()
periods = hourly_data['properties']['periods']

below_temp = []  # store all hours with temps below 40

# periods is hours, so this will go to 12 hours
for period in periods[:16]:
    # Parse and format time nicely
    time = datetime.fromisoformat(period['startTime'].replace('Z', '+00:00'))
    formatted_time = time.strftime('%a %I:%M %p')

    temp = period['temperature']
    tempUnit = period['temperatureUnit']
    #--------TESTING---------
    #print(f'{formatted_time} / {temp} {tempUnit}')

    # Check if below 70
    if temp <= 40:
        below_temp.append((temp, formatted_time))

# Report lowest temp if any are below 70
if below_temp:
    lowest_temp, time = min(below_temp, key=lambda x: x[0])
    send_email(f'Bring Orchids inside tonight. Lowest temp: {lowest_temp} F at {time}')
    #-------TESTING-------
    #print(f'\nBring plants inside! It will be below 70 F!')
    #print(f'Lowest temperature: {lowest_temp} F at {time}')
