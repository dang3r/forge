import os
import requests
from openai import OpenAI
import concurrent.futures

client = OpenAI()

# List of image prompts
objects = [
    "white siamese cat",
    "red rose with stem",
    "BMW supercar",
    "Mario from Super Mario Bros",
    "belgian malinois dog",
]

# Folder to save the images
output_folder = "/home/dang3r/dev/forge/generate-ornaments-from-text/images"
# make a directory even if it already exists
if not os.path.exists(output_folder):
    os.mkdir(output_folder)


# Define the number of workers
num_workers = 4

# Function to download and save the image
def download_and_save_image(object, index):
    prompt = f"a 3d model of a single (only one) {object} whose full body is visible from the front left. Make sure the side and back of the object is visible. Please only include the object and nothing else!"
    # Make API call to generate the image
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    print(f"Generated image for prompt: `{prompt}`")

    # Retrieve the image URL from the response
    image_url = response.data[0].url

    # Download the image from the URL
    image_data = requests.get(image_url).content

    # Save the image to a folder with a unique filename
    tokens = object.split()
    filename = f"{'_'.join(tokens)}.png"
    filepath = os.path.join(output_folder, filename)
    with open(filepath, "wb") as f:
        f.write(image_data)

# Create a ThreadPoolExecutor with the specified number of workers
with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    # Iterate over each image prompt
    for i, prompt in enumerate(objects):
        # Submit the download_and_save_image function as a task to the executor
        executor.submit(download_and_save_image, prompt, i)
