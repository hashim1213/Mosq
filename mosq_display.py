import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import hijri_converter
import requests  # To make API calls
import pytz


# Flask API URL to fetch data
API_URL = 'http://127.0.0.1:5000/data'

# API for sunrise and sunset times (replace with Brandon MB coordinates)
SUNSET_API_URL = "https://api.sunrise-sunset.org/json?lat=49.8485&lng=-99.9501&formatted=0"

# Initialize announcement_list to avoid NameError
announcement_list = []
announcement_index = 0
# timezone
brandon_tz = pytz.timezone('America/Winnipeg')

# Function to fetch sunset time
def get_sunset_time():
    try:
        response = requests.get(SUNSET_API_URL)
        if response.status_code == 200:
            data = response.json()
            sunset_time = data['results']['sunset']

            # Parse the sunset time without timezone
            sunset_dt_utc = datetime.strptime(sunset_time, '%Y-%m-%dT%H:%M:%S%z')  # Keep the timezone info here

            # Convert UTC time to local time (Brandon)
            sunset_dt_local = sunset_dt_utc.astimezone(brandon_tz)

            # Format the time to AM/PM format without leading zero
            return sunset_dt_local.strftime('%l:%M %p').strip()

        else:
            print(f"Failed to fetch sunset data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching sunset data: {e}")
        return None

# Function to fetch data from the API every 10 seconds
def fetch_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            update_ui(data)  # Update the UI with the new data
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching data: {e}")
    
    # Poll every 10 seconds (10000 milliseconds)
    root.after(10000, fetch_data)

# Function to update the UI based on fetched data
def update_ui(data):
    # Update prayer times
    for i, prayer_time in enumerate(prayer_time_labels):
        prayer, athan_label, iqamah_label = prayer_time
        if prayer == "Maghrib":
            sunset_time = get_sunset_time()
            if sunset_time:
                athan_label.config(text=sunset_time)  # Use sunset for Maghrib athan
                iqamah_time = (datetime.strptime(sunset_time, '%I:%M %p') + timedelta(minutes=10)).strftime('%I:%M %p')
                iqamah_label.config(text=iqamah_time)  # Iqamah is 10 minutes after sunset
        else:
            athan_label.config(text=datetime.strptime(data[f'{prayer.lower()}Athan'], '%H:%M').strftime('%I:%M %p'))
            iqamah_label.config(text=datetime.strptime(data[f'{prayer.lower()}Iqamah'], '%H:%M').strftime('%I:%M %p'))
    
    # Update Quran verse with a smaller font size
    quran_verse_label.config(text=f"\n{data['quranVerse']}", wraplength=600)

    # Update announcements with multi-line support
    global announcement_list
    announcement_list = data['announcements'].split(',')

    # Update donation message
    donation_message.config(text=f"{data['donationMessage']}\n\nDonate via e-Transfer:")

    # Update phone silence message
    silence_label.config(text=data['phoneMessage'])

# Function to update the current time dynamically with seconds
def update_time():
    current_time = datetime.now().strftime('%I:%M:%S %p')
    time_label.config(text=current_time)
    root.after(1000, update_time)  # Update every second

# Function to get the Islamic date
def get_islamic_date():
    today = datetime.now()
    hijri_date = hijri_converter.Gregorian(today.year, today.month, today.day).to_hijri()
    return f"{hijri_date.day} {hijri_date.month_name()} {hijri_date.year}"

# Function to rotate announcements
def update_announcement():
    global announcement_index
    if announcement_list:  # Ensure announcement_list is not empty
        announcement_label.config(text=f"{announcement_list[announcement_index]}")
        announcement_index = (announcement_index + 1) % len(announcement_list)
    root.after(5000, update_announcement)  # Change announcement every 5 seconds

# Create the main window
root = tk.Tk()
# Make the window full screen
root.attributes('-fullscreen', True)

root.title("MOSQ Prayer Time Display") #Title
root.geometry("1000x600")  # Scaled-down window size for smaller screens
root.configure(bg="#002B5B")  # Deep blue background for a professional look

# Load and resize the logo image
logo_image = Image.open("final_logo3.png")  # Load the image
logo_image = logo_image.resize((1050, 200), Image.LANCZOS)  # Resize for smaller window
logo_photo = ImageTk.PhotoImage(logo_image)

# Logo Section (resizable, always at the top)
header_frame = tk.Frame(root, bg="#002B5B")
header_frame.pack(fill="x")

logo_label = tk.Label(header_frame, image=logo_photo, bg="#002B5B")
logo_label.pack(fill="x", pady=10)

# Right Side Section for Clock, Quran, and Announcements
right_side_frame = tk.Frame(root, bg="#F5F5F5", padx=10, pady=10)  # Light background for contrast
right_side_frame.pack(fill="both", expand=True, side="right")

# Current Time Section (big and bold) and Date below
clock_frame = tk.Frame(right_side_frame, bg="#F5F5F5")
clock_frame.pack(fill="both", expand=True, side="top", pady=10)

# Big, bold current time
time_label = tk.Label(clock_frame, text="", font=("Arial", 80, "bold"), fg="black", bg="#F5F5F5")  # Larger time font
time_label.pack(pady=5)  # Reduced padding

# Date (Gregorian and Islamic) below the time
date_label = tk.Label(clock_frame, text=f"October 23, 2024 | {get_islamic_date()}", 
                      font=("Arial", 24, "bold"), fg="black", bg="#F5F5F5")
date_label.pack(pady=0)  # Remove extra space

# Quran Verses Section (below the clock, smaller size, reduced padding)
quran_frame = tk.Frame(right_side_frame, bg="#F5F5F5")
quran_frame.pack(fill="both", expand=True, side="top", pady=5)  # Reduced vertical padding

quran_verse_label = tk.Label(quran_frame, text="Quran Verse:\nLoading...", 
                             font=("Arial", 24, "italic"), bg="#F5F5F5", fg="#002B5B", justify="center", wraplength=600)
quran_verse_label.pack(pady=5, padx=10)  # Reduced top padding

# Prayer Times Section (left side, takes up half the screen, larger fonts)
prayer_frame = tk.Frame(root, bg="#F5F5F5", padx=10, pady=10)  # Light background for contrast
prayer_frame.pack(fill="both", expand=True, side="left")

# Title section for the prayer times table
header = tk.Label(prayer_frame, text="Prayer   |  Athan  |   Iqamah", font=("Arial", 36, "bold"), bg="#F5F5F5", fg="black")
header.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

# Display prayer times (initially placeholders, will be updated by API)
prayers = ["Fajr", "Zuhr", "Asr", "Maghrib", "Isha", "Jumuah"]
prayer_time_labels = []

for i, prayer in enumerate(prayers):
    bg_color = "#d9edf7" if prayer == "Jumuah" else "white"  # Highlight Jumuah
    prayer_label = tk.Label(prayer_frame, text=prayer, font=("Arial", 36, "bold"), bg=bg_color, fg="black", width=10, anchor="w")
    athan_label = tk.Label(prayer_frame, text="Loading...", font=("Arial", 36, "bold"), bg=bg_color, fg="black", width=10, anchor="center")
    iqamah_label = tk.Label(prayer_frame, text="Loading...", font=("Arial", 36, "bold"), bg=bg_color, fg="black", width=10, anchor="center")

    prayer_label.grid(row=i+1, column=0, padx=5, pady=5)
    athan_label.grid(row=i+1, column=1, padx=5, pady=5)
    iqamah_label.grid(row=i+1, column=2, padx=5, pady=5)
    
    prayer_time_labels.append((prayer, athan_label, iqamah_label))

# Message to silence phones under prayer times
silence_label = tk.Label(prayer_frame, text="Please silence your phones", 
                         font=("Arial", 24), fg="red", bg="#F5F5F5")
silence_label.grid(row=len(prayers)+1, column=0, columnspan=3, pady=10)

# Announcements Section with polished rounded rectangle
announcement_frame = tk.Frame(right_side_frame, bg="#F5F5F5")
announcement_frame.pack(fill="both", expand=True, side="bottom", pady=(10, 0))  # Reduced padding

# Create a rounded rectangle for announcements using relief and bd for rounded effect
announcement_container = tk.Frame(announcement_frame, bg="#F5F5F5", padx=10, pady=10, relief="groove", bd=2)
announcement_container.pack(fill="both", padx=10, pady=5)  # Reduced padding

announcement_label = tk.Label(announcement_container, text=" Loading announcements...", 
                              font=("Arial", 24), fg="black", bg="#F5F5F5", justify="center", wraplength=400)
announcement_label.pack(pady=10)

# Donation Message with border box, moved under silence message
donation_container = tk.Frame(prayer_frame, bg="#d9edf7", padx=15, pady=15, relief="groove", bd=3)
donation_container.grid(row=len(prayers)+2, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

donation_message = tk.Label(donation_container, text="Loading donation message...", 
                            font=("Arial", 20, "bold"), fg="black", bg="#d9edf7", justify="center")
donation_message.pack(pady=10)

# Start the time and announcement update
update_time()
update_announcement()

# Fetch data from the API and update the UI every 10 seconds (Polling)
fetch_data()

# Exit full screen on 'Escape' key press
root.bind('<Escape>', lambda event: root.attributes('-fullscreen', False))

# Run the main event loop
root.mainloop()
