import streamlit as st

# Function to convert text to uppercase
def convert_to_uppercase(text):
    return text.upper()

# Streamlit App
def main():
    # Title of the app
    st.title("Text File Uppercase Converter")

    # Create a textbox for input text
    st.write("Paste your text here:")
    input_text = st.text_area("Input Text", height=200)

    # Create a button to trigger the conversion
    if st.button("Convert"):
        if input_text:
            # Call the conversion function
            output_text = convert_to_uppercase(input_text)

            # Display the output on the right side
            st.write("### Converted Text:")
            st.text_area("Output Text", output_text, height=200)
        else:
            st.write("Please paste some text to convert.")

# Run the Streamlit app
if __name__ == "__main__":
    main()
