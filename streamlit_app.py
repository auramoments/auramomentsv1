import streamlit as st
from openai import OpenAI
import base64
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading

# Initialize OpenAI client and set the API key from Streamlit secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=openai_api_key)
GPT_MODEL = "gpt-4o"
DALLE_MODEL = "dall-e-3"

# Function to encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Function to generate an image using DALL-E 3
def generate_aura_image(description):
    prompt = (
        f"Create a high-fidelity, circular aura image that exudes a sense of energy and {description}. "
        "The aura should be a gradient, using only various shades of random color that seamlessly blend into one another. "
        "Start with a light, pastel shade of random color at the outermost edge, gradually transitioning to a vibrant, mid-tone shade in the middle, "
        "and finally, a deep, rich shade of random color at the innermost part of the circle. "
        "The transition between the shades should be smooth and refined, creating a polished, high-quality finish. "
        "The image should be centered on a black background to make the random color tones pop and to add depth and contrast to the overall composition."
    )

    response = client.images.generate(
        model=DALLE_MODEL,
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )

    return response.data[0].url

# Path to your TikTok verification file
verification_file_path = 'tiktokK3jS5DxkwT6dmdBmroH3Xyp31Gvu90Me.txt'

class FileHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == f'/{verification_file_path}':
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            with open(verification_file_path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_error(404, "File not found")

def start_server():
    server = HTTPServer(('0.0.0.0', 8000), FileHandler)
    server.serve_forever()

# Start the server in a new thread
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# Streamlit app
def main():
    st.title("Image Description Generator")

    # File uploader
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Convert the file to an image path
        image_path = "temp_image.jpg"  # Temporary file path
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Encode the image to base64
        base64_image = encode_image(image_path)

        # Display the image
        st.image(image_path, caption='Uploaded Image', use_column_width=True)

        # Generate description using OpenAI GPT-4o
        if st.button("Generate Description"):
            # Use the client to make a request with the specified model
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that responds in Markdown. Describe the following image."},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Please describe the following image:"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
                ],
                temperature=0.0,
            )
            description = response.choices[0].message.content.strip()
            st.session_state['description'] = description  # Store the description in session state
            st.write("Description:")
            st.write(description)

    # Generate aura image using DALL-E 3
    if 'description' in st.session_state:
        if st.button("Generate Aura Image"):
            with st.spinner("Generating aura image..."):
                aura_image_url = generate_aura_image(st.session_state['description'])
            st.image(aura_image_url, caption='Generated Aura Image', use_column_width=True)

    # Provide the URL for TikTok verification file
    st.write("TikTok verification file is being served at:")
    st.write(f"[http://localhost:8000/{verification_file_path}](http://localhost:8000/{verification_file_path})")

if __name__ == "__main__":
    main()
