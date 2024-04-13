import tensorflow as tf
import streamlit as st
from PIL import Image, ImageOps
import numpy as np

# Load the pre-trained model
model = tf.keras.models.load_model('./handwrittendigit.h5')

def prepare_image_for_prediction(original_img):
    """Prepares an image for optimal prediction by the model."""

    grayscale_img = ImageOps.grayscale(original_img)

    if grayscale_img.mode in ('RGBA', 'LA', 'P'):
        grayscale_img = grayscale_img.convert('RGB')

    inverted_img = ImageOps.invert(grayscale_img)

    max_dimension = 28 
    aspect_ratio = max_dimension / max(inverted_img.size)
    new_size = tuple(int(d * aspect_ratio) for d in inverted_img.size)
    resized_img = inverted_img.resize(new_size, Image.BICUBIC)

    diff = (max_dimension - resized_img.width, max_dimension - resized_img.height)
    padded_img = ImageOps.expand(resized_img, border=diff, fill='black')

    img_array = np.array(padded_img).astype(np.float32) / 255.0
    img_array = img_array.reshape(-1, 28, 28, 1) 
    return img_array

def predict(image):
    processed_image = prepare_image_for_prediction(image)
    predictions = model.predict(processed_image)
    return np.argmax(predictions), np.max(predictions)

# App
st.title('Image Classifier')
st.write("Upload an image to predict.")

uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg'])
if uploaded_file is not None:
    image = Image.open(uploaded_file)

    st.image(image, caption='Uploaded Image', use_column_width=True)
    if st.button('Predict'):

        label, confidence = predict(image)
        st.write(f'Predicted Digit: {label}')
        st.write(f'confidence {confidence:.2f}')
