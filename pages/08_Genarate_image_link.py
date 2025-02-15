import streamlit as st
import requests
import base64

# Set ImgBB API Key
IMGBB_API_KEY = "ec519cb1c1643a46e16f22fe58a256cb"
UPLOAD_URL = "https://api.imgbb.com/1/upload"

# Streamlit UI
st.title("Genarate Image Link")

# Upload Button
uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Convert image to base64
    image_bytes = uploaded_file.read()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    # Upload to ImgBB
    response = requests.post(
        UPLOAD_URL,
        data={
            "key": IMGBB_API_KEY,
            "image": encoded_image
        },
    )

    # Process response
    if response.status_code == 200:
        data = response.json()
        image_url = data["data"]["url"]

        # Show the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        # Display the shareable link
        st.success("Image uploaded successfully!")
        #st.text_input("Shareable Link (Copy Manually):", image_url)

        # Copy Button (Works natively in Streamlit)
        st.code(image_url, language="")

    else:
        st.error("Failed to upload image. Please try again.")
