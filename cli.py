import os
import threading
import time

import pygame
import speech_recognition as sr

import database


class TeluguBusInfoCLI:
    def __init__(self):
        # Initialize pygame for audio playback
        pygame.init()
        pygame.mixer.init()
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # State variables
        self.is_recording = False
        self.timer_count = 15
        
        # Connect to database
        try:
            import pymysql
            self.connection = pymysql.connect(
                host=database.DATABASE_HOST,
                user=database.DATABASE_USER,
                password=database.DATABASE_PASSWORD,
                database=database.DATABASE_NAME
            )
            print("Connected to database successfully")
        except Exception as e:
            print(f"Database connection error: {e}")
            self.connection = None
    
    def display_menu(self):
        """Display the main menu and get user choice"""
        while True:
            print("\n" + "="*50)
            print("Telugu Bus Information System - CLI Version")
            print("="*50)
            print("1. Record Audio Query (15 seconds max)")
            print("2. Exit")
            
            choice = input("\nEnter your choice (1-2): ")
            
            if choice == '1':
                self.start_recording()
            elif choice == '2':
                print("Exiting program. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def start_recording(self):
        """Start recording audio from the microphone"""
        self.is_recording = True
        self.timer_count = 15
        
        # Start timer thread
        timer_thread = threading.Thread(target=self.update_timer)
        timer_thread.daemon = True
        timer_thread.start()
        
        print("\nRecording started. Speak now... (recording will stop after 15 seconds)")
        print("Press Ctrl+C at any time to stop recording early.")
        
        try:
            self.record_audio()
        except KeyboardInterrupt:
            print("\nRecording stopped by user.")
            self.is_recording = False
    
    def update_timer(self):
        """Update the countdown timer"""
        while self.is_recording and self.timer_count > 0:
            time.sleep(1)
            self.timer_count -= 1
            print(f"\rTime remaining: {self.timer_count}s", end="", flush=True)
            
        # Auto-stop recording if timer reaches zero
        if self.timer_count <= 0 and self.is_recording:
            self.is_recording = False
            print("\nTime's up! Processing your query...")
    
    def record_audio(self):
        """Record audio and process it"""
        try:
            with self.microphone as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Recording... Speak your query now.")
                
                # Wait while is_recording is True
                audio = self.recognizer.listen(source, timeout=15, phrase_time_limit=15)
                
                print("\nProcessing your query...")
                self.process_audio(audio)
                
        except sr.WaitTimeoutError:
            print("No speech detected")
        except Exception as e:
            print(f"Error recording audio: {e}")
    
    def process_audio(self, audio):
        """Process the recorded audio using the database module"""
        try:
            # Send to database.send_to_llm which handles the LLM interaction
            json_response = database.send_to_llm()
            
            if json_response:
                print("Query analyzed successfully")
                self.process_json_response(json_response)
            else:
                print("Failed to process query")
        except Exception as e:
            print(f"Error processing query: {e}")
    
    def process_json_response(self, json_response):
        """Process the JSON response and call appropriate database function"""
        try:
            module_name = json_response.get('Module Name')
            print(f"Identified intent: {module_name}")
            
            match module_name:
                case "Bus_Enquiry_Next_Bus":
                    database.Bus_Enquiry_Next_Bus(
                        json_response.get('Source_City'), 
                        json_response.get('Destination_City'), 
                        json_response.get('Bus_Type', 'none'), 
                        json_response.get('Service_Number', 'none'), 
                        json_response.get('Time_Frame', 'none'), 
                        json_response.get('Seat_Availability', 'none')
                    )
                case "Bus_Enquiry_Last_Bus":
                    database.Bus_Enquiry_Last_Bus(
                        json_response.get('Source_City'), 
                        json_response.get('Destination_City'), 
                        json_response.get('Bus_Type', 'none'), 
                        json_response.get('Service_Number', 'none'), 
                        json_response.get('Last_Departure_Time', 'none')
                    )
                case "Fare_Enquiry":
                    database.Fare_Enquiry(
                        json_response.get('Source_City'), 
                        json_response.get('Destination_City'), 
                        json_response.get('Bus_Type', 'none'),
                        json_response.get('Fare_Amount', 'none'), 
                        json_response.get('Booking_Options', 'none')
                    )
                case "Platform_Enquiry":
                    database.Platform_Enquiry(
                        json_response.get('Source_City'), 
                        json_response.get('Destination_City', 'none'),
                        json_response.get('Bus_Number', 'none'), 
                        json_response.get('Service_Number', 'none')
                    )
                case "Seat_Availability_Enquiry":
                    database.Seat_Availability_Enquiry(
                        json_response.get('Source_City'), 
                        json_response.get('Destination_City'), 
                        json_response.get('Bus_Type', 'none'), 
                        json_response.get('Seat_Status', 'none')
                    )
                case "Luggage_Enquiry":
                    database.Luggage_Enquiry(
                        json_response.get('Source_City'), 
                        json_response.get('Destination_City'), 
                        json_response.get('Weight', '0')
                    )
                case "Bus_Status_Enquiry":
                    database.Bus_Status_Enquiry(
                        json_response.get('Source_City'), 
                        json_response.get('Bus_Number', 'none'), 
                        json_response.get('Service_Number', 'none'), 
                        json_response.get('Expected_Delay', 'none')
                    )
                case "Multiple_City_Enquiry":
                    database.Multiple_City_Enquiry(
                        json_response.get('Source_City'), 
                        json_response.get('Intermediate_City', 'none'), 
                        json_response.get('Destination_City'), 
                        json_response.get('Bus_Type', 'none')
                    )
                case "Special_Service_Enquiry":
                    database.Special_Service_Enquiry(
                        json_response.get('Source_City'), 
                        json_response.get('Destination_City'), 
                        json_response.get('Festival_Special_Occasion', 'none')
                    )
                case _:
                    print(f"Unknown module: {module_name}")
        except Exception as e:
            print(f"Error in processing response: {e}")
    
    def on_closing(self):
        """Clean up resources when closing the application"""
        if self.connection:
            self.connection.close()
        pygame.quit()


if __name__ == "__main__":
    app = TeluguBusInfoCLI()
    try:
        app.display_menu()
    finally:
        app.on_closing()
