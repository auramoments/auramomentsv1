import streamlit as st
from openai import OpenAI
import base64

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

    # Serve the TikTok signature file from the app
    with open("tiktokndPG5VVum7NRmpmSIi8TC9KZdngW9ujE.txt", "r") as f:
        signature_file = f.read()
    st.markdown(f"[Download signature file](/{signature_file})")

if __name__ == "__main__":
    main()
