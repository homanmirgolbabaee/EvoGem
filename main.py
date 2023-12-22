import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import os
import streamlit as st 
import base64
from PIL import Image
import io
import cam
from cam import record_video_and_screenshots
import serial
from cam import generate









# Function to set up authentication
def authenticate_with_service_account(json_credentials_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_credentials_path



def record_and_upload():
    # Call the function to record video and capture screenshots
    cam.record_video_and_screenshots()  # This function should encapsulate the logic from cam.py

    # Upload the captured content to GCS
    cam.upload_to_gcs('lablabhack', 'screenshots')  # Update with your bucket name




    
    
# Function to convert image to base64
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Function to call Gemini Pro Vision API
def generate(image_base64,user_input):
    authenticate_with_service_account("json/gemini-lablab-28e6c232bf0d.json")
    model = GenerativeModel("gemini-pro-vision")
    image_part = Part.from_data(data=base64.b64decode(image_base64), mime_type="image/png")
    
    full_description = ""  # Initialize an empty string to hold the full description

    responses = model.generate_content(
        [f"""you are a helpful visual assistant you are precise and short.describe the following command {user_input} focus on the object than its background. keep it very short and precise as a visual tool detection.""", image_part],
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32
        },
        stream=True,
    )
    
    for response in responses:
        part_description = response.candidates[0].content.parts[0].text
        st.write(part_description)
        full_description += part_description + " "  # Concatenate each part of the description

    # Save the full description to a file
    with open('description.txt', 'w') as file:
        file.write(full_description.strip())  # Remove any leading/trailing whitespace
        
    # Run the script to transfer the file to the Pico
    # script_path = 'transfer_to_pico.bat'  # or 'path\\to\\transfer_to_pico.bat' on Windows
    # subprocess.run(script_path, shell=True)
    print(full_description.strip())
    return full_description.strip()  # Return the full description
    
    
# Function to call Gemini Pro
def multiturn_generate_content(prompt):
    authenticate_with_service_account("json/gemini-lablab-28e6c232bf0d.json")

    config = {
        "max_output_tokens": 2048,
        "temperature": 0.9,
        "top_p": 1
    }
    model = GenerativeModel("gemini-pro")
    chat = model.start_chat()
    response = chat.send_message(prompt, generation_config=config)
    print(response.text)
    return response.text  # Return the response text

import serial
import time

def initializing_nodeMCU(string):
    # Open serial port (Replace 'COM4' with your ESP8266's COM port)'
    ser = serial.Serial('COM4', 9600, timeout=1)
    time.sleep(2)  # Wait for the connection to initialize

    # Convert the string to bytes and send it to the ESP8266
    data_to_send = (str(string) + "!\n").encode()  # Encoding the string to bytes
    ser.write(data_to_send)

    time.sleep(5.5)  # Short delay to ensure the data is fully sent
    ser.close()  # Close the serial port

    
# Function to call Chatbot Interface
def chatbot_interface():

    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Replace or augment this part with your chat function
    if prompt := st.chat_input("Your question"): # Prompt for user input
        st.session_state.messages.append({"role": "user", "content": prompt})
        response_text = multiturn_generate_content(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response_text}) # Add response to message history
        
        print("respones:"+str(response_text))
        
        initializing_nodeMCU(response_text)
    
    for message in st.session_state.messages: # Display the prior chat messages
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
    

def resize_image(image, base_width=300):
    """
    Resize the image to a specified width while maintaining aspect ratio.
    """
    w_percent = (base_width / float(image.size[0]))
    h_size = int((float(image.size[1]) * float(w_percent)))
    return image.resize((base_width, h_size), Image.ANTIALIAS)




def process_and_generate(image):
    # Convert the UploadedFile to a PIL Image object
    pil_image = Image.open(image)

    # Save the image to a BytesIO object
    buffered = io.BytesIO()
    pil_image.save(buffered, format="JPEG")  # Use JPEG for the format
    image_base64 = base64.b64encode(buffered.getvalue()).decode()

    # Call the generate function from cam module
    return cam.generate(image_base64)

# Streamlit page configuration and initialization
st.set_page_config(page_title="Chatbot", page_icon="🤖")
# Sidebar for navigation
def main():
    
    menu = st.sidebar.selectbox("Menu", ["Home", "Chatbot","Image","Video"])

    # Routing based on sidebar selection
    if menu == "Home":
        st.title("Welcome to the Home Page")
        st.write("Interfacing Gemini Pro & Gemini Pro-Vision with IoT (NodeMCU)")
        st.write("github.com/homanmirgolbabaee")
        st.write("**COOL FEATURES COMMING SOON !**")
        st.subheader("Options")
        st.write("-**Chatbot** : Chat with Gemini Pro on a NodeMCU & 0.96 OLED Display ")
        st.write("**")

            
    if menu == "Image":
        st.title("Stream/Via Webcam")
        st.write("Capture an image using your webcam and get it described.")

        col1, col2 = st.columns([3, 2])  # Adjust column widths for better layout

        with col1:
            st.subheader("Capture Image")
            webcam_image = st.camera_input("Take a picture")

            # Initialize session state for recording
            if 'recording_started' not in st.session_state:
                st.session_state.recording_started = False

            def start_recording():
                st.session_state.recording_started = True
                with st.spinner("Recording and uploading..."):
                    record_and_upload()
                    st.success("Recording and upload completed!")
                    st.session_state.recording_started = False
            user_input = st.text_input("Enter your text here:")   
            
            if user_input:
                if webcam_image:
                    describe_button = st.button("Describe Image", help="Click to analyze the captured image.")
                    if describe_button:
                        with st.spinner("Analyzing the image..."):
                            # Read the content of the uploaded file
                            image_data = webcam_image.read()

                            # Use PIL to open the image data
                            pil_image = Image.open(io.BytesIO(image_data))

                            # Save the PIL image to a BytesIO object
                            buffered = io.BytesIO()
                            pil_image.save(buffered, format="JPEG")

                            image_base64 = base64.b64encode(buffered.getvalue()).decode()
                                # Streamlit text input component
                    
                            result = generate(image_base64,user_input)            
                            initializing_nodeMCU(result)
            


        with col2:
            st.subheader("Instructions")

            
            with st.expander("Instructions", expanded=True):
                st.write("""
                    - Take a Photo.
                    - Type Your Command .
                    - Click **Describe Image**.
                """)
            st.markdown("---")  # Adds a horizontal line for visual separation
            
    if menu == "Video":
        st.title("Video Recgnition ")
                
        record_button = st.button("Record and Upload", help="Record a video and upload it.")
        if record_button and not st.session_state.recording_started:
            start_recording()
            
            
    elif menu == "Chatbot":
        
        st.title("Chatbot Interface")
        chatbot_interface()
        
        with st.expander("Instructions", expanded=True):
            st.write("""
                - Ask anything.
                - See Result on Device
            """)
        st.markdown("---")  # Adds a horizontal line for visual separation  
          
if __name__ == "__main__":
    main()