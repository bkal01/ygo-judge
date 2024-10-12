import os
import requests
import json

# Define the base URL and directory path
base_url = "https://db.ygoresources.com/data/qa/"
directory_path = "data/ygoresources/yugioh-qa-history"

# Get a list of filenames in the directory
filenames = os.listdir(directory_path)

# Loop through each filename
for filename in filenames:
    # Extract the ID from the filename (removing .json)
    qa_id = filename.replace(".json", "")
    
    # Construct the full URL for the API request
    url = f"{base_url}{qa_id}"
    
    # Send a GET request to fetch the JSON data
    response = requests.get(url)
    
    if response.status_code == 200:
        # Get the JSON response
        response_data = response.json()
        
        # Save the response JSON in the corresponding file
        save_path = os.path.join(directory_path, filename)
        with open(save_path, "w") as json_file:
            json.dump(response_data, json_file, indent=4)
        
        print(f"Saved {qa_id}.json successfully.")
    else:
        print(f"Failed to retrieve data for ID {qa_id}. Status code: {response.status_code}")
