import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import database as db
import pygame
import threading
import time
import os
import sys
from ttkthemes import ThemedTk

class VoiceBusEnquiryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RTC Bus Voice Enquiry System")
        self.root.geometry("1000x800")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("Voice.TButton", 
                           font=("Helvetica", 20, "bold"), 
                           padding=20)
        self.style.configure("Status.TLabel", 
                           font=("Helvetica", 14),
                           foreground="blue")
        self.style.configure("Timer.TLabel", 
                           font=("Helvetica", 16, "bold"),
                           foreground="red")
        
        # Main container
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top section - Voice control
        voice_frame = ttk.Frame(main_frame)
        voice_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title = ttk.Label(voice_frame, 
                         text="RTC Bus Voice Enquiry System",
                         font=("Helvetica", 24, "bold"))
        title.pack(pady=(0, 20))
        
        # Instructions
        instructions = ttk.Label(voice_frame,
                               text="Press and hold the button while speaking your query in Telugu",
                               font=("Helvetica", 12))
        instructions.pack(pady=(0, 20))
        
        # Example queries
        examples = """Example queries you can ask:
        - "హైదరాబాద్ కి తదుపరి బస్సు ఎప్పుడు?"
        - "విజయవాడ నుండి తిరుపతి కి చివరి బస్సు ఏ సమయంలో?"
        - "ఏసీ బస్సు టికెట్ ఎంత?"
        - "220 బస్సు ఏ ప్లాట్‌ఫారం నుండి వస్తుంది?"
        """ 
        
        examples_label = ttk.Label(voice_frame,
                                 text=examples,
                                 font=("Helvetica", 12),
                                 justify=tk.LEFT)
        examples_label.pack(pady=(0, 20))
        
        # Voice control frame
        voice_control_frame = ttk.Frame(voice_frame)
        voice_control_frame.pack(pady=20)
        
        # Voice button
        self.voice_button = ttk.Button(voice_control_frame,
                                     text="🎤 Click to Start",
                                     style="Voice.TButton")
        self.voice_button.pack(side=tk.LEFT, padx=10)
        self.voice_button.bind('<ButtonPress-1>', self.start_recording)
        self.voice_button.bind('<ButtonRelease-1>', self.stop_recording)
        
        # Reset button
        self.reset_button = ttk.Button(voice_control_frame,
                                     text="🔄 Reset Conversation",
                                     style="Voice.TButton",
                                     command=self.reset_conversation)
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        # Status and timer labels
        self.status_label = ttk.Label(voice_frame,
                                    text="Ready to listen...",
                                    style="Status.TLabel")
        self.status_label.pack(pady=(0, 10))
        
        self.timer_label = ttk.Label(voice_frame,
                                   text="",
                                   style="Timer.TLabel")
        self.timer_label.pack()
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create output text widget with custom font for Telugu
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            font=("Noto Sans Telugu", 12),
            height=20
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Recording state
        self.is_recording = False
        self.timer_thread = None
        
        # Initialize pygame for audio playback
        pygame.init()
        pygame.mixer.init()
        
        # Redirect stdout to capture database.py output
        sys.stdout = self
        
        # Add conversation state
        self.conversation_started = False
        
    def write(self, text):
        """Redirect stdout to the text widget"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        
    def flush(self):
        """Required for stdout redirection"""
        pass
        
    def start_recording(self, event):
        """Start voice recording"""
        if not self.conversation_started:
            self.conversation_started = True
            # Play greeting message and wait for it to finish
            if not db.play_greeting():
                messagebox.showerror("Error", "Failed to play greeting message")
                return
            
        self.is_recording = True
        self.voice_button.configure(text="🎙️ Recording... Release when done")
        self.status_label.configure(text="Listening to your query...")
        self.output_text.delete(1.0, tk.END)
        self.start_time = time.time()
        
        # Start timer in separate thread
        self.timer_thread = threading.Thread(target=self.update_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
    def stop_recording(self, event):
        """Stop recording and process the query"""
        self.is_recording = False
        self.voice_button.configure(text="🎤 Click ") # and Hold to Speak")
        self.status_label.configure(text="Processing your query...")
        self.timer_label.configure(text="")
        
        # Process the voice input in a separate thread
        threading.Thread(target=self.process_voice_input).start()
        
    def update_timer(self):
        """Update the recording timer"""
        while self.is_recording:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.configure(text=f"Recording: {elapsed}s")
            time.sleep(0.1)
            
    def process_voice_input(self):
        """Process voice input and execute database query"""
        try:
            # Get voice input result
            result = db.send_to_llm()
            if not result:
                self.status_label.configure(text="Could not understand. Please try again.")
                return
                
            # Connect to database
            connection = db.pymysql.connect(
                host=db.DATABASE_HOST,
                user=db.DATABASE_USER,
                password=db.DATABASE_PASSWORD,
                database=db.DATABASE_NAME
            )
            
            # Set connection in database module
            db.connection = connection
            
            try:
                # Execute the appropriate query based on the module name
                module_name = result['Module Name']
                self.status_label.configure(text=f"Executing {module_name}...")
                
                match module_name:
                    case "Bus_Enquiry_Next_Bus":
                        db.Bus_Enquiry_Next_Bus(
                            result['Source_City'],
                            result['Destination_City'],
                            result.get('Bus_Type', 'none'),
                            result.get('Service_Number', 'none'),
                            result.get('Time_Frame'),
                            result.get('Seat_Availability')
                        )
                    case "Bus_Enquiry_Last_Bus":
                        db.Bus_Enquiry_Last_Bus(
                            result['Source_City'],
                            result['Destination_City'],
                            result.get('Bus_Type', 'none'),
                            result.get('Service_Number', 'none'),
                            result.get('Last_Departure_Time', 'none')
                        )
                    case "Fare_Enquiry":
                        db.Fare_Enquiry(
                            result['Source_City'],
                            result['Destination_City'],
                            result.get('Bus_Type', 'none'),
                            result.get('Fare_Amount'),
                            result.get('Booking_Options')
                        )
                    case "Platform_Enquiry":
                        db.Platform_Enquiry(
                            result['Source_City'],
                            result['Destination_City'],
                            result.get('Bus_Number', 'none'),
                            result.get('Service_Number', 'none')
                        )
                    case "Seat_Availability_Enquiry":
                        db.Seat_Availability_Enquiry(
                            result['Source_City'],
                            result['Destination_City'],
                            result.get('Bus_Type', 'none'),
                            result.get('Seat_Status')
                        )
                    case "Luggage_Enquiry":
                        db.Luggage_Enquiry(
                            result['Source_City'],
                            result['Destination_City'],
                            result.get('Weight')
                        )
                    case "Bus_Status_Enquiry":
                        db.Bus_Status_Enquiry(
                            result['Source_City'],
                            result.get('Bus_Number'),
                            result.get('Service_Number'),
                            result.get('Expected_Delay')
                        )
                    case "Multiple_City_Enquiry":
                        db.Multiple_City_Enquiry(
                            result['Source_City'],
                            result.get('Intermediate_City'),
                            result['Destination_City'],
                            result.get('Bus_Type')
                        )
                    case "Special_Service_Enquiry":
                        db.Special_Service_Enquiry(
                            result['Source_City'],
                            result['Destination_City'],
                            result.get('Festival_Special_Occasion')
                        )
                    case _:
                        print("Invalid module selection.")
                
                self.status_label.configure(text="Ready to listen...")
                
                
            finally:
                connection.close()
                
        except Exception as e:
            self.status_label.configure(text="An error occurred. Please try again.")
            messagebox.showerror("Error", str(e))
            
    def reset_conversation(self):
        """Reset the conversation state"""
        self.conversation_started = False
        self.output_text.delete(1.0, tk.END)
        self.status_label.configure(text="Ready to start new conversation...")
        self.voice_button.configure(text="🎤 Click to Start")
        
def main():
    # Ensure the Audio directory exists
    os.makedirs(r"C:\Audio", exist_ok=True)
    
    # Create and run the GUI
    root = ThemedTk(theme="arc")
    app = VoiceBusEnquiryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 