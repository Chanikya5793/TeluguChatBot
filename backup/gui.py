import os
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk

import pygame
import speech_recognition as sr
from PIL import Image, ImageTk

import database


class TeluguBusInfoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Telugu Bus Information System")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize pygame for audio playback
        pygame.init()
        pygame.mixer.init()
        
        # State variables
        self.is_recording = False
        self.toggle_mode = False
        self.timer_count = 15
        self.timer_active = False
        
        # Create the GUI components
        self.create_widgets()
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Database connection
        self.connection = None
        self.connect_to_database()
    
    def connect_to_database(self):
        """Connect to the database using credentials from database module"""
        try:
            import pymysql
            self.connection = pymysql.connect(
                host=database.DATABASE_HOST,
                user=database.DATABASE_USER,
                password=database.DATABASE_PASSWORD,
                database=database.DATABASE_NAME
            )
            self.log_message("Connected to database successfully")
        except Exception as e:
            self.log_message(f"Database connection error: {e}", error=True)
    
    def create_widgets(self):
        """Create all GUI components"""
        # Create main frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Telugu Bus Information System", 
                              font=("Arial", 24, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 20))
        
        # Response display area
        self.response_frame = tk.LabelFrame(main_frame, text="Conversation", bg="#f0f0f0", 
                                           font=("Arial", 12))
        self.response_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.response_area = scrolledtext.ScrolledText(self.response_frame, wrap=tk.WORD, 
                                                     font=("Arial", 12), bg="white",
                                                     height=15)
        self.response_area.pack(fill="both", expand=True, padx=5, pady=5)
        self.response_area.config(state="disabled")
        
        # Control frame
        control_frame = tk.Frame(main_frame, bg="#f0f0f0")
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Toggle switch for record mode
        self.toggle_var = tk.BooleanVar()
        self.toggle_check = tk.Checkbutton(control_frame, text="Toggle Mode", 
                                         variable=self.toggle_var,
                                         command=self.toggle_record_mode,
                                         bg="#f0f0f0", font=("Arial", 12))
        self.toggle_check.pack(side="left", padx=(0, 20))
        
        # Timer display
        self.timer_label = tk.Label(control_frame, text="15s", font=("Arial", 16), 
                                  bg="#f0f0f0", width=3)
        self.timer_label.pack(side="left", padx=(0, 20))
        
        # Record button
        self.record_button = tk.Button(control_frame, text="Hold to Record", 
                                     font=("Arial", 14, "bold"), 
                                     bg="#4CAF50", fg="white",
                                     activebackground="#45a049",
                                     width=15, height=2)
        self.record_button.pack(side="left", padx=10)
        
        # Bind button events
        self.record_button.bind("<ButtonPress-1>", self.start_recording)
        self.record_button.bind("<ButtonRelease-1>", self.stop_recording)
        
        # Status indicator
        self.status_frame = tk.Frame(control_frame, bg="#f0f0f0")
        self.status_frame.pack(side="left", padx=20)
        
        self.status_indicator = tk.Canvas(self.status_frame, width=20, height=20, 
                                        bg="#f0f0f0", highlightthickness=0)
        self.status_indicator.pack(side="left")
        self.status_indicator.create_oval(2, 2, 18, 18, fill="gray", outline="")
        
        self.status_label = tk.Label(self.status_frame, text="Ready", 
                                   font=("Arial", 12), bg="#f0f0f0")
        self.status_label.pack(side="left", padx=5)
        
        # Clear button
        self.clear_button = tk.Button(main_frame, text="Clear Conversation", 
                                    command=self.clear_conversation,
                                    font=("Arial", 12))
        self.clear_button.pack(pady=10)
    
    def toggle_record_mode(self):
        """Switch between hold-to-record and toggle modes"""
        self.toggle_mode = self.toggle_var.get()
        if self.toggle_mode:
            self.record_button.config(text="Click to Record")
        else:
            self.record_button.config(text="Hold to Record")
    
    def start_recording(self, event=None):
        """Start recording audio"""
        if self.is_recording:
            return
        
        # If in toggle mode, button click toggles recording state
        if self.toggle_mode:
            if self.is_recording:
                self.stop_recording()
                return
        
        self.is_recording = True
        self.update_status("Recording", "red")
        self.timer_active = True
        self.timer_count = 15
        
        # Start timer thread
        timer_thread = threading.Thread(target=self.update_timer)
        timer_thread.daemon = True
        timer_thread.start()
        
        # Start recording thread
        recording_thread = threading.Thread(target=self.record_audio)
        recording_thread.daemon = True
        recording_thread.start()
    
    def stop_recording(self, event=None):
        """Stop recording audio"""
        # In toggle mode, button press controls start/stop
        if self.toggle_mode and event is not None:
            if not self.is_recording:
                self.start_recording()
                return
        # If not in toggle mode, stop only on button release
        elif not self.toggle_mode and event is not None:
            self.is_recording = False
            self.timer_active = False
            self.update_status("Processing...", "orange")
    
    def update_timer(self):
        """Update the countdown timer"""
        while self.timer_active and self.timer_count > 0:
            self.timer_label.config(text=f"{self.timer_count}s")
            time.sleep(1)
            self.timer_count -= 1
            
        # Auto-stop recording if timer reaches zero
        if self.timer_count <= 0 and self.is_recording:
            self.is_recording = False
            self.timer_active = False
            self.root.after(0, lambda: self.update_status("Processing...", "orange"))
    
    def record_audio(self):
        """Record audio and process it"""
        try:
            with self.microphone as source:
                self.log_message("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.log_message("Speak now...")
                
                # Wait while is_recording is True
                audio = self.recognizer.listen(source, timeout=15, phrase_time_limit=15)
                
                if not self.is_recording:  # Check if recording was manually stopped
                    self.root.after(0, lambda: self.process_audio(audio))
        except sr.WaitTimeoutError:
            self.log_message("No speech detected", error=True)
            self.root.after(0, lambda: self.update_status("Ready", "gray"))
        except Exception as e:
            self.log_message(f"Error recording audio: {e}", error=True)
            self.root.after(0, lambda: self.update_status("Ready", "gray"))
    
    def process_audio(self, audio):
        """Process the recorded audio using the database module"""
        self.log_message("Processing your query...")
        try:
            # Send to database.send_to_llm which handles the LLM interaction
            json_response = database.send_to_llm()
            
            if json_response:
                self.log_message("Query analyzed successfully")
                self.process_json_response(json_response)
            else:
                self.log_message("Failed to process query", error=True)
        except Exception as e:
            self.log_message(f"Error processing query: {e}", error=True)
        finally:
            self.update_status("Ready", "gray")
    
    def process_json_response(self, json_response):
        """Process the JSON response and call appropriate database function"""
        try:
            module_name = json_response.get('Module Name')
            self.log_message(f"Identified intent: {module_name}")
            
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
                    self.log_message(f"Unknown module: {module_name}", error=True)
        except Exception as e:
            self.log_message(f"Error in processing response: {e}", error=True)
    
    def log_message(self, message, error=False):
        """Add a message to the response area"""
        self.response_area.config(state="normal")
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        
        # Format based on message type
        if error:
            self.response_area.insert(tk.END, f"[{timestamp}] ERROR: {message}\n\n", "error")
            self.response_area.tag_config("error", foreground="red")
        else:
            self.response_area.insert(tk.END, f"[{timestamp}] {message}\n\n")
        
        self.response_area.see(tk.END)  # Scroll to the end
        self.response_area.config(state="disabled")
    
    def update_status(self, status_text, color):
        """Update the status indicator and label"""
        self.status_indicator.create_oval(2, 2, 18, 18, fill=color, outline="")
        self.status_label.config(text=status_text)
    
    def clear_conversation(self):
        """Clear the conversation history"""
        self.response_area.config(state="normal")
        self.response_area.delete(1.0, tk.END)
        self.response_area.config(state="disabled")
        self.log_message("Conversation cleared")
    
    def on_closing(self):
        """Clean up resources when closing the application"""
        if self.connection:
            self.connection.close()
        pygame.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TeluguBusInfoGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
