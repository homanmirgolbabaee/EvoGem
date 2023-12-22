import cv2
import time
import os
from google.cloud import storage
from google.cloud.storage import transfer_manager
from pathlib import Path
import streamlit as st 

def record_video_and_screenshots():

    # Define the duration of the video and interval for screenshots
    record_duration = 5  # seconds
    screenshot_interval = 1  # seconds

    # Create a directory for screenshots if it doesn't exist
    screenshots_dir = 'screenshots'
    os.makedirs(screenshots_dir, exist_ok=True)

    # Initialize the video capture object (1 for the external webcam, change if necessary)
    cap = cv2.VideoCapture(0)

    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('video/output.mp4', fourcc, 20.0, (640, 480))

    start_time = time.time()
    next_screenshot_time = start_time + screenshot_interval
    screenshot_count = 0

    while True:
        current_time = time.time()
        ret, frame = cap.read()
        if ret:
            # Write the frame into the file 'output.avi'
            out.write(frame)

            # Capture screenshot at defined intervals
            if current_time >= next_screenshot_time and screenshot_count < 5:
                screenshot_filename = os.path.join(screenshots_dir, f'screenshot_{screenshot_count + 1}.png')
                cv2.imwrite(screenshot_filename, frame)
                screenshot_count += 1
                next_screenshot_time += screenshot_interval

            # Show the frame (optional, you can remove this if you don't need a preview)
            cv2.imshow('frame', frame)

            # Break the loop after 'record_duration' seconds
            if current_time - start_time > record_duration:
                break
        else:
            break

    # Release everything when done
    cap.release()
    out.release()
    cv2.destroyAllWindows()


from google.cloud import storage
# Function to set up authentication
def authenticate_with_service_account(json_credentials_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_credentials_path
    
    
def upload_to_gcs(bucket_name, source_directory):
    authenticate_with_service_account("json/gemini-lablab-28e6c232bf0d.json")
    """Uploads files in a directory to Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Generate a list of file paths in the source directory
    directory_as_path_obj = Path(source_directory)
    file_paths = list(directory_as_path_obj.rglob("*"))

    # Filter to include only files, not directories
    file_paths = [path for path in file_paths if path.is_file()]

    # Convert paths to strings relative to the source directory
    relative_paths = [str(path.relative_to(source_directory)) for path in file_paths]

    # Start the concurrent upload
    results = transfer_manager.upload_many_from_filenames(
        bucket, relative_paths, source_directory=source_directory, max_workers=8
    )

    # Process results
    for name, result in zip(relative_paths, results):
        if isinstance(result, Exception):
            print("Failed to upload {} due to exception: {}".format(name, result))
        else:
            print("Uploaded {} to {}.".format(name, bucket.name))

# ... [rest of your webcam and screenshot code]

# After capturing screenshots, upload them to GCS
#bucket_name = 'lablahack'  # Replace with your GCS bucket name
#upload_to_gcs(bucket_name, 'screenshots')



import base64
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part

def generate(image_path,user_input):
    authenticate_with_service_account("json/gemini-lablab-28e6c232bf0d.json")
    model = GenerativeModel("gemini-pro-vision")

    # Read the image file as binary data
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # Convert the binary data to base64-encoded data
    base64_encoded_data = base64.b64encode(image_data)
    
    # Determine the MIME type based on the file extension (you might want to improve this)
    if image_path.lower().endswith('.png'):
        mime_type = 'image/png'
    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        mime_type = 'image/jpeg'
    else:
        raise ValueError("Unsupported image format")

    # Create the Part object using base64 decoded data
    image_part = Part.from_data(data=base64.b64decode(base64_encoded_data), mime_type=mime_type)
   
    responses = model.generate_content(
        [image_part, f"""you are a helpful visual assistant. can you describe {user_input} what you see only the object. you should only describe the object not its background."""],
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32
        },
    )

    print(responses)
    
# Specify the path to your image file in the screenshots folder
#screenshot_path = 'test_objects/glasses.jpg'  # Update with the correct file name
#generate(screenshot_path)



import base64
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part

def vid_description_generate(video_path):
    authenticate_with_service_account("json/gemini-lablab-28e6c232bf0d.json")
    model = GenerativeModel("gemini-pro-vision")

    # Read the video file as binary data
    with open(video_path, 'rb') as video_file:
        video_data = video_file.read()

    # Convert the binary data to base64-encoded data
    base64_encoded_data = base64.b64encode(video_data)

    # Create the Part object using base64 decoded data
    video_part = Part.from_data(data=base64.b64decode(base64_encoded_data), mime_type="video/mp4")

    responses = model.generate_content(
        [video_part, """What is the person in the video doing?"""],
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32
        },
        stream=True,
    )
  
    for response in responses:
        print(response.candidates[0].content.parts[0].text)

#vid_description_generate('video/output.mp4')



# Function to call Gemini Pro Vision API
def quiz_generate(image_base64):
    authenticate_with_service_account("json/gemini-lablab-28e6c232bf0d.json")
    model = GenerativeModel("gemini-pro-vision")
    image_part = Part.from_data(data=base64.b64decode(image_base64), mime_type="image/png")
    
    full_description = ""  # Initialize an empty string to hold the full description

    responses = model.generate_content(
        ["""you are a helpful visual assistant you are precise and short.describe the following object and focus on the object than its background. keep it very short and precise as a visual tool detection.""", image_part],
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



