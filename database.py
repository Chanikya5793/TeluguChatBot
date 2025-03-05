import datetime
import decimal
import json
import os
import time

import google.generativeai as genai
# Replace playsound with pygame (which we already use)
# from playsound import playsound
import pygame
import pymysql
import pyttsx3
import speech_recognition as sr
from google.cloud import texttospeech
from gtts import gTTS
from jinja2 import Template
from pydub import AudioSegment


def generate_mp3_gtts(text, lang, output_filepath):
    """Generates an MP3 file using gTTS and saves it to the specified location."""
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(output_filepath)
        print(f"MP3 file saved successfully to: {output_filepath}")
        return True #Indicate success
    except Exception as e:
        print(f"Error: Failed to generate MP3 file. {e}")
        return False #Indicate failure

#Example usage

# ... (Configuration, database functions, audio input function - same as before)
DATABASE_HOST = "localhost"
DATABASE_USER = "root"
DATABASE_PASSWORD = "abc123"  # Replace with your actual password
DATABASE_NAME = "Buses"  # Replace with your database name
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")


# Example usage:
def fare_row(row):
    amount, currency, bus_type, bus_reg, departure_time, route_name, source_city, dest_city = row
    template_str = """
    {{ source_city }} నుండి {{ dest_city }} కి వెళ్ళే {{ bus_type }} బస్సు ({{ bus_reg }}) యొక్క ఛార్జీ {{ amount }} రూపాయలు. 
    బస్సు బయలుదేరే సమయం {{ departure_time }}.
    """

    template = Template(template_str)

    paragraph = template.render(
        amount=row[0], currency=row[1], bus_type=row[2], bus_reg=row[3],
        route_name=row[5], source_city=row[6], dest_city=row[7], departure_time=row[4]
    )
    return paragraph
def next_row(row):
    schedule_id, departure_time, bus_reg, bus_type, route_name, source_city, dest_city = row
    template_str = """
    {{ source_city }} నుండి {{ dest_city }} కి వెళ్ళే {{ bus_type }} బస్సు ({{ bus_reg }}) బయలుదేరే సమయం {{ departure_time }}.
    """

    template = Template(template_str)

    paragraph = template.render(
        schedule_id=row[0], departure_time=row[1], bus_reg=row[2], bus_type=row[3],
        source_city=row[5], dest_city=row[6], route_name=row[4]
    )
    return paragraph
def last_row(row):
    departure_time,bus_reg,bus_type,route_name,source_city,dest_city = row
    template_str = """
    {{ source_city }} నుండి {{ dest_city }} కి వెళ్ళే {{ bus_type }} బస్సు ({{ bus_reg }}) బయలుదేరే సమయం {{ departure_time }}.
    """

    template = Template(template_str)

    paragraph = template.render(
        departure_time=row[0], bus_reg=row[1], bus_type=row[2],
        source_city=row[4], dest_city=row[5], route_name=row[3]
    )
    return paragraph
def platform_row(row):
    departure_time, bus_reg, bus_type, platform_number,route_name, source_city,dest_city = row
    print(departure_time)
    template_str = """
    {{ source_city }} నుండి {{ dest_city }} కి వెళ్ళే {{ bus_type }} బస్సు ({{ bus_reg }}) {{platform_number}}వ  ప్లాట్ఫారంలొ  ఆగుతుంది . 
    """

    template = Template(template_str)

    paragraph = template.render(
        platform_number=row[3], route_name=row[4], bus_type=row[2], bus_reg=row[1], source_city=row[5], dest_city=row[6], departure_time=row[0]
    )
    return paragraph
def execute_query(conn, query, params=None):
    """Execute a SQL query."""
    cursor = None
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor
    except pymysql.Error as e:
        print(f"Error executing query: {e}")
        return None
def fetch_data(cursor):
    """Fetches all data from a cursor, or None on error"""
    try:
        if cursor:
            return cursor.fetchall()
        else:
            return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
def timedelta_to_hhmm(timedelta_obj):
    """Converts a datetime.timedelta object to HH:MM format."""
    if isinstance(timedelta_obj, datetime.timedelta):
        total_seconds = int(timedelta_obj.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    else:
        return timedelta_obj
def Bus_Enquiry_Next_Bus(Source_City, Destination_City, Bus_Type, Service_Number, Time_Frame=None, Seat_Availability=None):
    query = """SELECT s.schedule_id, s.departure_time, b.bus_registration_number, b.bus_type, r.route_name, st_src.stop_name AS source_stop_name, st_dst.stop_name AS destination_stop_name
    FROM Schedules s
    JOIN Routes r ON s.route_id = r.route_id
    JOIN Buses b ON s.bus_id = b.bus_id
    JOIN Stops st_src ON r.source_stop_id = st_src.stop_id
    JOIN Stops st_dst ON r.destination_stop_id = st_dst.stop_id
    WHERE st_src.city = %s AND st_dst.city = %s"""

    params = [Source_City, Destination_City]
    print(1)
    if Bus_Type!='none':
        query += " AND b.bus_type = %s"
        params.append(Bus_Type)
    if Service_Number!='none':
        query += " AND b.bus_registration_number = %s"
        params.append(Service_Number)


    query += " ORDER BY s.departure_time"
    cursor = execute_query(connection, query,params)
    text=""
    if cursor:
        results = fetch_data(cursor)
        if results:
            for row in results:
                modified_row = tuple(timedelta_to_hhmm(item) if isinstance(item, datetime.timedelta) else item for item in row)
                print(modified_row)
                text += next_row(modified_row)
        lang = "te"
        output_filepath = r"C:\Audio\next.mp3"
        print(text)
        print("Converting text to speech")
        generate_mp3_gtts(text, lang, output_filepath)
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(output_filepath)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():  # Wait until the music finishes playing
            pygame.time.Clock().tick(10)
    

def Bus_Enquiry_Last_Bus(Source_City,Destination_City, Bus_Type, Service_Number, Last_Departure_Time):
    query="""select
    s.departure_time,
    b.bus_registration_number,
    b.bus_type,
    r.route_name,
    source_stop.city AS source_city,
    dest_stop.city AS destination_city
FROM Schedules s
JOIN Buses b ON s.bus_id = b.bus_id
JOIN Routes r ON s.route_id = r.route_id
JOIN Stops source_stop ON r.source_stop_id = source_stop.stop_id
JOIN Stops dest_stop ON r.destination_stop_id = dest_stop.stop_id
WHERE source_stop.city = %s AND dest_stop.city = %s"""
    params = [Source_City, Destination_City]
    if Bus_Type!='none':
        query += " AND b.bus_type = %s"
        params.append(Bus_Type)
    if Service_Number!='none':
        query += " AND b.bus_registration_number = %s"
        params.append(Service_Number)
    if Last_Departure_Time!='none':
        query += " AND s.departure_time <= %s"
        try:
            time = datetime.datetime.strptime(Last_Departure_Time, "%H:%M").time()
            params.append(time)
            print(time)
        except ValueError:
            print(f"Invalid time format: {time_str}. Expected HH:MM.")

    query += " ORDER BY s.departure_time DESC"
    cursor = execute_query(connection, query,params)
    text=""
    if cursor:
        results = fetch_data(cursor)
        if results:
            for row in results:
                modified_row = tuple(timedelta_to_hhmm(item) if isinstance(item, datetime.timedelta) else item for item in row)
                print(modified_row)
                text += last_row(modified_row)
        lang = "te"
        output_filepath = r"C:\Audio\last.mp3"
        print(text)
        print("Converting text to speech")
        generate_mp3_gtts(text, lang, output_filepath)
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(output_filepath)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():  # Wait until the music finishes playing
            pygame.time.Clock().tick(10)
    
def Fare_Enquiry(Source_City, Destination_City, Bus_Type, Fare_Amount, Booking_Options):
    query="""
SELECT
    f.amount,
    f.currency,
    b.bus_type,
    b.bus_registration_number,
    s.departure_time,
    r.route_name,
    source_stop.city AS source_city,
    dest_stop.city AS destination_city
FROM Fares f
JOIN Routes r ON f.route_id = r.route_id
JOIN Schedules s ON r.route_id = s.route_id  -- Join with Schedules table
JOIN Buses b ON s.bus_id = b.bus_id  -- Join with Buses table using s.bus_id
JOIN Stops source_stop ON r.source_stop_id = source_stop.stop_id
JOIN Stops dest_stop ON r.destination_stop_id = dest_stop.stop_id
WHERE source_stop.city = %s AND dest_stop.city = %s;"""
    params = [Source_City, Destination_City]
    cursor = execute_query(connection, query,params)
    text=""
    if cursor:
        results = fetch_data(cursor)
        if results:
            for row in results:
                modified_row=(int(row[0]),) + row[1:]
                modified_row=tuple(timedelta_to_hhmm(item) if isinstance(item, datetime.timedelta) else item for item in modified_row)
                print(modified_row)
                text += fare_row(modified_row)
        lang = "te"
        output_filepath = r"C:\Audio\output.mp3"
        print(text)
        print("Converting text to speech")
        generate_mp3_gtts(text, lang, output_filepath)
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(output_filepath)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():  # Wait until the music finishes playing
            pygame.time.Clock().tick(10)
def Platform_Enquiry(Source_City, Destination_City, Bus_Number, Service_Number):
    query="""select s.departure_time, b.bus_registration_number, b.bus_type,
    source_stop.platform_number,
    r.route_name,
    source_stop.city AS source_city,
    dest_stop.city AS destination_city
FROM Schedules s
JOIN Buses b ON s.bus_id = b.bus_id
JOIN Routes r ON s.route_id = r.route_id
JOIN Stops source_stop ON r.source_stop_id = source_stop.stop_id
JOIN Stops dest_stop ON r.destination_stop_id = dest_stop.stop_id
WHERE source_stop.city = %s"""
    params = [Source_City]
    if Destination_City!='none':
        query += " AND dest_stop.city = %s"
        params.append(Destination_City)
    if Bus_Number!='none':
        query += " AND b.bus_registration_number = %s"
        params.append(Bus_Number)
    if Service_Number!='none':
        query += " AND b.bus_registration_number = %s"
        params.append(Service_Number)

    query += " ORDER BY s.departure_time"
    cursor = execute_query(connection, query,params)
    text=""
    if cursor:
        results = fetch_data(cursor)
        if results:
            for row in results:
                modified_row = tuple(timedelta_to_hhmm(item) if isinstance(item, datetime.timedelta) else item for item in row)
                print(modified_row)
                text += platform_row(modified_row)
        lang = "te"
        output_filepath = r"C:\Audio\platform.mp3"
        print(text)
        print("Converting text to speech")
        generate_mp3_gtts(text, lang, output_filepath)
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(output_filepath)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():  # Wait until the music finishes playing
            pygame.time.Clock().tick(10)
    

def Seat_Availability_Enquiry(Source_City, Destination_City, Bus_Type, Seat_Status):
    query="""select
    s.schedule_id,
    b.bus_registration_number,
    b.bus_type,
    r.route_name,
    source_stop.city AS source_city,
    dest_stop.city AS destination_city,
    b.bus_capacity,
    (b.bus_capacity - (select COUNT(*) FROM bookings WHERE bookings.schedule_id = s.schedule_id)) AS seats_available
FROM Schedules s
JOIN Buses b ON s.bus_id = b.bus_id
JOIN Routes r ON s.route_id = r.route_id
JOIN Stops source_stop ON r.source_stop_id = source_stop.stop_id
JOIN Stops dest_stop ON r.destination_stop_id = dest_stop.stop_id
WHERE source_stop.city = %s AND dest_stop.city = %s
"""
    params = [Source_City, Destination_City]
    cursor = execute_query(connection, query,params)
    if cursor:
        results = fetch_data(cursor)
        if results:
            for row in results:
                print(row)


def Luggage_Enquiry(Source_City, Destination_City, Weight):
    query="""SELECT
    s_source.city AS source_city,
    s_dest.city AS destination_city,
    r.distance_km AS distance_km,
    b.bus_type,
    lp.allowed_weight_kg,
    lp.extra_charge_per_kg,
    lp.parcel_cost_per_kg
FROM
    Routes r
JOIN
    Stops s_source ON r.source_stop_id = s_source.stop_id
JOIN
    Stops s_dest ON r.destination_stop_id = s_dest.stop_id
JOIN
    Schedules sc ON r.route_id = sc.route_id
JOIN
    Buses b ON sc.bus_id = b.bus_id
JOIN
    LuggagePolicies lp ON b.bus_type = lp.bus_type
where s_source.city=%s and s_dest.city=%s"""
    params = [Source_City, Destination_City]
    cursor = execute_query(connection, query,params)
    if cursor:
        results = fetch_data(cursor)
        if results:
            for row in results:
                print(row)
                kg=int(row[4])
                cost=int(row[6])
                dist=int(row[2])
                Weight=int(Weight)
                if Weight<=kg:
                    price=Weight*cost*dist
                else:
                    price=Weight*cost*dist+(kg-Weight)*int(row[5])
                print(price)
def Bus_Status_Enquiry(Source_City="Vijayawada", Bus_Number=None, Service_Number=None, Expected_Delay=None):
    query="""select
    s.schedule_status,
    s.departure_time,
    b.bus_registration_number,
    r.route_name,
    source_stop.city AS source_city,
    dest_stop.city AS destination_city
FROM Schedules s
JOIN Buses b ON s.bus_id = b.bus_id
JOIN Routes r ON s.route_id = r.route_id
JOIN Stops source_stop ON r.source_stop_id = source_stop.stop_id
JOIN Stops dest_stop ON r.destination_stop_id = dest_stop.stop_id
WHERE source_stop.city = COALESCE(@Source_City, 'Vijayawada')
  AND (b.bus_registration_number = @Bus_Number OR @Bus_Number IS NULL)
  AND (b.bus_registration_number = @Service_Number OR @Service_Number IS NULL);"""
    cursor = execute_query(connection, query)
    if cursor:
        results = fetch_data(cursor)
        if results:
            for row in results:
                print(row)

def Multiple_City_Enquiry(Source_City=None, Intermediate_City=None, Destination_City=None, Bus_Type=None):
    query="""select
    s.departure_time,
    b.bus_registration_number,
    b.bus_type,
    r.route_name,
    source_stop.city AS source_city,
    dest_stop.city AS destination_city
FROM Schedules s
JOIN Buses b ON s.bus_id = b.bus_id
JOIN Routes r ON s.route_id = r.route_id
JOIN Stops source_stop ON r.source_stop_id = source_stop.stop_id
JOIN Stops dest_stop ON r.destination_stop_id = dest_stop.stop_id
WHERE source_stop.city = @Source_City
  AND dest_stop.city = @Destination_City
  AND b.bus_type = COALESCE(@Bus_Type, b.bus_type);"""
    cursor = execute_query(connection, query)
    if cursor:
        results = fetch_data(cursor)
        if results:
            for row in results:
                print(row)

def Special_Service_Enquiry(Source_City="Vijayawada", Destination_City=None, Festival_Special_Occasion=None):
    pass

    

# --- LLM Interaction (using Gemini - Direct SQL) ---
def send_to_llm():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        try:
            audio = r.listen(source, timeout=10)  # Timeout after 10 seconds
            text = r.recognize_google(audio, language="te-IN")  # Specify Telugu
            print("You said: " + text)
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print("Could not request results from speech recognition service; {0}".format(e))
            return None
        except sr.WaitTimeoutError:
            print("Listening timed out. No speech detected.")
            return None
    genai.configure(api_key="AIzaSyAjwl7thjLDRZGKBazfq_b1BzWX-tN-0BU")

    model = genai.GenerativeModel("gemini-1.5-flash")  # Or "gemini-pro"
    audio_data = audio.get_wav_data()  # get wav data.
    mime_type = "audio/wav"  # Speech_recognition returns wav.
    contents = {
            "mime_type": "audio/wav",  # Adjust mime type accordingly (e.g., audio/mp3)
            "data": audio_data,
    }
    print("calling API")
    prompt = """
    Hey Gemini, I am sending an audio clip containing a real-time bus-related enquiry. The primary language of the clip is Telugu, but it may also include words in English and Hindi.
This bot will be physically placed at the Vijayawada Bus Stand, so by default, the source city is Vijayawada, unless the user explicitly mentions another city.
If the user mentions multiple cities (excluding Vijayawada), the bot should switch to the Multiple_City_Enquiry module to ensure proper handling.

Task
Analyze the real-time enquiry and:
Identify the intent (bus enquiry, fare enquiry, platform details, etc.).
Extract the relevant parameters from the audio.
Return the response in a structured JSON format.

Modules with Real-time Examples & Parameters

1) Next Bus Enquiry (Real-time & Expanded)
Module: Bus_Enquiry_Next_Bus
Parameters:
Source_City (Default: Vijayawada)
Destination_City
Bus_Type
Service_Number (if mentioned)
Time_Frame (if the user asks for a specific time)
Seat_Availability (if asked)
Example Queries:
"Next Super Luxury bus to Hyderabad?"
"When is the next Deluxe bus to Guntur?"
"Is there an Express bus to Tirupati in the next hour?"
"2509 service number bus Vijayawada nunchi vastundaa?"
"Hyderabad nunchi Vijayawada ki next bus eppudu?" (Source is not default)
"గుంటూరు వెళ్ళే వోల్వో బస్సు ఏది?"
"Afternoon lo Nellore ki Deluxe bus vastundaa?"
"Hyderabad lo airport nunchi direct RTC bus undha?"

2) Last Bus Enquiry
Module: Bus_Enquiry_Last_Bus
Parameters:
Source_City (Default: Vijayawada)
Destination_City
Bus_Type
Service_Number
Last_Departure_Time
Example Queries:
"padinti lopu kakani bus"
"Delhi ki akhari bus"
"What time was the last Amaravati bus to Rajahmundry?"
"2509 service number last bus yappudu vellindhi?"
"What bus is there before 5:00 for Tirupati"
"Chennai ki chivari bus"
"Last AC bus to Tirupati from Hyderabad?" (Source is not default)
3) Real-time Fare Enquiry
Module: Fare_Enquiry
Parameters:
Source_City (Default: Vijayawada)
Destination_City
Bus_Type
Fare_Amount (if asked)
Booking_Options (if asked)
Example Queries:
"How much is the ticket from Vijayawada to Guntur?"
"What is the fare for AC bus from Vijayawada to Chennai?"
"Hyderabad nunchi Vizag ki AC bus fare entha?" (Source is not default)
4) Real-time Platform Enquiry
Module: Platform_Enquiry
Parameters:
Source_City (Default: Vijayawada)
City_Name (if user asks about another city's platform)
Bus_Number
Service_Number
Example Queries:
"Which platform does Bus No. 220 start from in Vijayawada?"
"2509 service bus ki Hyderabad lo platform number entha?"
"Vizag lo RTC bus stand lo Tirupati bus ekkada undi?" (Source is not default)

5) Seat Availability & Booking
Module: Seat_Availability_Enquiry
Parameters:
Source_City (Default: Vijayawada)
Destination_City
Bus_Type
Seat_Status
Example Queries:
"Hyderabad ki AC Sleeper lo seats available unnaya?"
"Tirupati ki sleeper bus lo konchem seats undhaa?"
"Last row lo sleeper beds Hyderabad bus lo available undhaa?"

6) Luggage & Goods Transport
Module: Luggage_Enquiry
Parameters:
Source_City (Default: Vijayawada)
Destination_City
Weight
Charges
Example Queries:
"Express bus lo 30 kg luggage allow chesthara?"
"Bangalore ki parcel pampadam ki charges entha?"
For output no need to give units just give values
7) Bus Status Enquiry
Module: Bus_Status_Enquiry
Parameters:
Source_City (Default: Vijayawada)
Bus_Number
Service_Number
Expected_Delay
Example Queries:
"Has the Super Luxury bus from Vijayawada to Hyderabad been delayed?"
"2509 service number bus delay avuthunda?"

8) Multi-City Enquiry (if multiple cities are mentioned)
Module: Multiple_City_Enquiry
Parameters:
Source_City
Intermediate_City
Destination_City
Bus_Type
Example Queries:
"What is the bus availability from Hyderabad to Tirupati?"
"Is there a bus from Chennai to Bangalore?"

9) Special Service Enquiry
Module: Special_Service_Enquiry
Parameters:
Source_City (Default: Vijayawada)
Destination_City
Festival/Special Occasion
Example Queries:
"Diwali ki extra special bus undhaa Hyderabad ki?"
"Eid ki extra RTC bus services unnaya?"

Expected JSON Output Format
{
  "Module Name": "Identified Module",
  "Parameter 1": "Extracted Value 1",
  "Parameter 2": "Extracted Value 2 (if applicable)",
  "Source_City": "Extracted Source City (Default: Vijayawada if not mentioned)",
  "Destination_City": "Extracted Destination City",
  "Service_Number": "Extracted Service Number (if mentioned)",
  "Seat_Availability": "Yes/No (if asked)",
  "Time_Frame": "Extracted Time Frame (In HH:MM)"
}
If parameter is not mentioned mention the parameter and keep value as none
    """

    try:
        response = model.generate_content([prompt, contents], stream=False)

    except Exception as e:
        print(f"Gemini API error: {e}")
        return None, None
    try:
            # 1. Access the text part of the response
            response_text = response.candidates[0].content.parts[0].text

            # 2. Extract the JSON string (remove ```json and ```)
            json_string = response_text.replace("```json\n", "").replace("\n```", "")

            # 3. Parse the JSON string into a Python dictionary
            json_data = json.loads(json_string)  # Use json.loads()

            print(json_data)  # Return the Python dictionary
            return json_data
    except (IndexError, json.JSONDecodeError) as e:
        print(f"Error processing Gemini response: {e}")
        print("Raw Gemini Response:", response) # print the raw response for debugging.

# --- Main Execution ---
if __name__ == "__main__":
    c=send_to_llm()
    try:
        connection = pymysql.connect(
            host=DATABASE_HOST,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            database=DATABASE_NAME
        )
        b=c['Module Name']
        match b:
            case "Bus_Enquiry_Next_Bus":
                Bus_Enquiry_Next_Bus(c['Source_City'], c['Destination_City'], c['Bus_Type'], c['Service_Number'], c['Time_Frame'], c['Seat_Availability'])
            case "Bus_Enquiry_Last_Bus":
                Bus_Enquiry_Last_Bus(c['Source_City'], c['Destination_City'], c['Bus_Type'], c['Service_Number'], c['Last_Departure_Time'])
            case "Fare_Enquiry":
                Fare_Enquiry(c['Source_City'], c['Destination_City'], c['Bus_Type'], c['Fare_Amount'], c['Booking_Options'])
            case "Platform_Enquiry":
                Platform_Enquiry(c['Source_City'], c['Destination_City'], c['Bus_Number'], c['Service_Number'])
            case "Seat_Availability_Enquiry":
                Seat_Availability_Enquiry(c['Source_City'], c['Destination_City'], c['Bus_Type'], c['Seat_Status'])
            case "Luggage_Enquiry":
                Luggage_Enquiry(c['Source_City'], c['Destination_City'], c['Weight'])
            case "Bus_Status_Enquiry":
                Bus_Status_Enquiry(c['Source_City'], c['Bus_Number'], c['Service_Number'], c['Expected_Delay'])
            case "Multiple_City_Enquiry":
                Multiple_City_Enquiry(c['Source_City'], c['Intermediate_City'], c['Destination_City'], c['Bus_Type'])
            case "Special_Service_Enquiry":
                Special_Service_Enquiry(c['Source_City'], c['Destination_City'], c['Festival_Special_Occasion'])
            case _:
                print("Invalid module selection.")

        connection.close()
    except pymysql.Error as e:
        print(f"Database error: {e}")
