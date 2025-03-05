#!/usr/bin/env python3
import os
import sys
import json
import google.generativeai as genai

# Set the Gemini API key
os.environ["GEMINI_API_KEY"] = "AIzaSyAjwl7thjLDRZGKBazfq_b1BzWX-tN-0BU"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def print_header():
    """Display the application header"""
    print("\n" + "="*50)
    print("Telugu Bus Information System - Text Mode")
    print("="*50)
    print("Type your query in Telugu or English.")
    print("Type 'exit' to quit.\n")

def run_query(prompt):
    """Send text query to Gemini API"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        system_prompt = """
        You are a helpful bus information assistant for Telugu speakers.
        This bot will be physically placed at the Vijayawada Bus Stand, so by default, the source city is Vijayawada.
        Analyze the query and extract bus information intent and parameters.
        Return a structured JSON response with the module name and parameters.
        
        Modules: Bus_Enquiry_Next_Bus, Bus_Enquiry_Last_Bus, Fare_Enquiry, Platform_Enquiry, 
        Seat_Availability_Enquiry, Luggage_Enquiry, Bus_Status_Enquiry, Multiple_City_Enquiry, Special_Service_Enquiry
        
        Parameters should include Source_City (default: Vijayawada), Destination_City, Bus_Type, etc.
        """
        
        response = model.generate_content([system_prompt, prompt])
        
        # Try to extract JSON from the response
        response_text = response.text
        
        # Look for JSON in the response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                print("Could not parse JSON response.")
                print("Raw response:", response_text)
                return None
        else:
            print("No JSON found in response.")
            print("Raw response:", response_text)
            return None
            
    except Exception as e:
        print(f"Error querying Gemini API: {e}")
        return None

def format_response(json_data):
    """Format JSON response into readable text"""
    if not json_data or "Module Name" not in json_data:
        return "Sorry, I couldn't understand that query."
    
    module = json_data.get("Module Name")
    source = json_data.get("Source_City", "Vijayawada")
    destination = json_data.get("Destination_City", "Unknown")
    
    output = f"\nQuery type: {module}\n"
    output += f"From: {source} To: {destination}\n"
    
    # Add other relevant information
    if module == "Bus_Enquiry_Next_Bus":
        bus_type = json_data.get("Bus_Type", "any")
        time_frame = json_data.get("Time_Frame", "soon")
        output += f"Looking for next {bus_type} bus, departing {time_frame}\n"
        
    elif module == "Bus_Enquiry_Last_Bus":
        time = json_data.get("Last_Departure_Time", "tonight")
        output += f"Looking for last bus before {time}\n"
        
    elif module == "Fare_Enquiry":
        bus_type = json_data.get("Bus_Type", "regular")
        output += f"Checking fare for {bus_type} bus\n"
        
    # Add fake response data since we can't connect to the database
    output += "\n[SIMULATED DATABASE RESPONSE]\n"
    
    if module == "Bus_Enquiry_Next_Bus":
        output += f"Next bus from {source} to {destination}:\n"
        output += "Bus type: Super Luxury\n"
        output += "Departure: 14:30\n"
        output += "Platform: 3\n"
        
    elif module == "Fare_Enquiry":
        output += f"Fare from {source} to {destination}:\n"
        output += "Regular: ₹150\n"
        output += "AC: ₹250\n"
        output += "Super Luxury: ₹350\n"
        
    elif module == "Platform_Enquiry":
        output += f"Platform information for buses to {destination}:\n"
        output += "Regular buses: Platform 1\n"
        output += "Express buses: Platform 2\n"
        output += "Super Luxury: Platform 3\n"
    
    return output

def main():
    print_header()
    
    while True:
        user_input = input("\nYour query > ")
        
        if user_input.lower() == 'exit':
            print("Thank you for using Telugu Bus Information System. Goodbye!")
            break
            
        print("Processing your query...")
        json_response = run_query(user_input)
        
        if json_response:
            print("\nQuery analyzed successfully")
            print(json.dumps(json_response, indent=2))
            
            # Format and display a simulated response
            formatted_response = format_response(json_response)
            print(formatted_response)
        else:
            print("Failed to process query. Please try again.")

if __name__ == "__main__":
    main()
