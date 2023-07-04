import streamlit as st
from datetime import date, timedelta
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
import os
import base64
import cv2
import numpy as np
from deepface import DeepFace

# Global variables
reference_img = cv2.imread("faces/Screenshot 2023-05-23 034728.png")  # Use your own image here
face_match = False

# Function to check face match
def check_face(frame):
    global face_match
    try:
        if DeepFace.verify(frame, reference_img.copy())['verified']:
            face_match = True
        else:
            face_match = False
    except ValueError:
        face_match = False

# Function for face detection and matching
def detect_and_match_faces(image):
    global face_match
    face_match = False

    # Convert PIL image to OpenCV format
    img_cv = np.array(image.convert('RGB'))
    img_cv = cv2.cvtColor(img_cv, 1)

    # Perform face detection and matching
    check_face(img_cv)

    # Display result
    if face_match:
        st.write("MATCH!")
    else:
        st.write("NO MATCH!")


def create_download_link(file_path):
    with open(file_path, "rb") as file:
        file_content = file.read()
    base64_pdf = base64.b64encode(file_content).decode('utf-8')
    download_link = f'<a href="data:application/pdf;base64,{base64_pdf}" download>Download PDF</a>'
    return download_link


def generate_pdf(name, surname, relative, applicant_name, applicant_email, relative_name, relative_email,
                 aadhaar, gender, dob, official_doc, disability, photo, filename):
    pdf_path = os.path.join(os.getcwd(), filename)
    c = canvas.Canvas(pdf_path, pagesize=letter)

    # Add form data to the PDF
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, "Name: " + name)
    c.drawString(50, 730, "Surname: " + surname)
    c.drawString(50, 710, "Immediate Relative: " + relative)
    c.drawString(50, 690, "Applicant's Name: " + applicant_name)
    c.drawString(50, 670, "Applicant's Email: " + applicant_email)
    c.drawString(50, 650, "Relative's Name: " + relative_name)
    c.drawString(50, 630, "Relative's Email: " + relative_email)
    c.drawString(50, 610, "Aadhaar Number: " + aadhaar)
    c.drawString(50, 590, "Gender: " + gender)
    c.drawString(50, 570, "Date of Birth: " + str(dob))
    c.drawString(50, 550, "Official Document: " + official_doc)
    c.drawString(50, 530, "Disability: " + ", ".join(disability))

    # Add photo to the PDF
    if photo is not None:
        img = Image.open(photo)
        img_width, img_height = img.size
        aspect_ratio = img_height / img_width
        max_width = 200
        img_width = min(max_width, img_width)
        img_height = int(img_width * aspect_ratio)

        img = img.resize((img_width, img_height), Image.ANTIALIAS)
        img_path = os.path.join(os.getcwd(), "temp_photo.png")
        img.save(img_path, format="PNG")

        c.drawImage(img_path, 400, 500, width=img_width, height=img_height)

    # Save the PDF
    c.save()

    return pdf_path


def page2():
    st.title("Application Form")

    # Form inputs
    name = st.text_input("Name")
    surname = st.text_input("Surname")

    relatives = ['Father', 'Mother', 'Husband', 'Wife', 'Guardian']
    relative = st.selectbox("Immediate Relative", relatives)

    applicant_name = st.text_input("Applicant's Name")
    applicant_email = st.text_input("Applicant's Email")

    relative_name = st.text_input("Relative's Name")
    relative_email = st.text_input("Relative's Email")

    aadhaar = st.text_input("Aadhaar Number")

    genders = ['Male', 'Female', 'Other', 'Third Gender']
    gender = st.radio("Gender", genders)

    max_date = date.today() - timedelta(days=365 * 18)
    dob = st.date_input("Date of Birth", value=max_date, min_value=max_date - timedelta(days=365 * 100),
                        max_value=max_date)

    official_doc = st.text_input("Official Document")

    disabilities = ['Visual Impairment', 'Hearing Impairment', 'Mobility Impairment', 'Cognitive Impairment']
    disability = st.multiselect("Disability", disabilities)

    photo = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])

    terms = st.checkbox("I agree to the terms and conditions")

    # Submit button
    if terms and st.button("Submit"):
        conn = sqlite3.connect('application.db')
        c = conn.cursor()

        # Create table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS applications
                     (name TEXT, surname TEXT, relative TEXT, applicant_name TEXT, applicant_email TEXT,
                     relative_name TEXT, relative_email TEXT, aadhaar TEXT, gender TEXT, dob DATE,
                     official_doc TEXT, disability TEXT)''')

        # Insert form data into the database
        c.execute("INSERT INTO applications VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)",
                  (name, surname, relative, applicant_name, applicant_email, relative_name, relative_email,
                   aadhaar, gender, dob, official_doc, ', '.join(disability)))
        conn.commit()
        conn.close()

        # Perform face detection and matching
        detect_and_match_faces(Image.open(photo))

        if face_match:
            pdf_filename = f"{name}_{surname}_application.pdf"
            pdf_path = generate_pdf(name, surname, relative, applicant_name, applicant_email, relative_name,
                                    relative_email, aadhaar, gender, dob, official_doc, disability, photo, pdf_filename)

            st.success("Form submitted successfully!")

            # Download link for the generated PDF
            download_link = create_download_link(pdf_path)
            st.markdown(download_link, unsafe_allow_html=True)
        else:
            st.warning("Face does not match the reference image!")
            st.write("Please try again with a different photo.")


def page1():
    

    # Set page title and favicon
    st.set_page_config(page_title='Democracy Info', page_icon='🗳️')

    # Title and subtitle
    st.title('Welcome to Democracy Info')
    st.subheader('Learn about Elections, Voter Registration, and more!')

    # Indian Flag
    image = Image.open('indian_flag.png')
    st.image(image, caption='Indian Flag', use_column_width=True)

    # Indian Emblem
    image = Image.open('indian_emblem.png')
    st.image(image, caption='Indian Emblem', use_column_width=True)

    # Democracy Info
    st.header('Democracy Information')
    st.markdown('''Democracy in India is a vibrant and integral part of its political landscape. With a population  of over 1.3 billion people, India is the world's largest democracy. The democratic system in India is founded    on the principles of equality, freedom, and the right to participate in decision-making.

    India follows a parliamentary form of government where the President is the head of state, and the Prime    Minister is the head of government. The President is elected indirectly by an electoral college comprising     members of both houses of Parliament and state legislatures.

    The Indian democracy operates on the principle of universal suffrage, which means that all citizens aged 18 and     above have the right to vote. Elections are conducted regularly at the national, state, and local levels to     elect representatives to the Parliament, State Legislative Assemblies, and Local Bodies.

    The Election Commission of India is an independent constitutional body responsible for the conduct of free and  fair elections. It ensures the integrity of the electoral process, including voter registration, candidate   nominations, and the smooth execution of the voting process.

    Voter registration plays a crucial role in Indian democracy. It enables eligible citizens to exercise their     right to vote and participate in shaping the country's future. By registering as a voter, individuals can   actively contribute to the selection of their representatives and influence policy decisions.

    The benefits of voter registration in India are numerous. It allows citizens to have a say in the   decision-making process, influence policies and governance, and hold elected officials accountable. It is a   fundamental step towards realizing the principles of democracy and ensuring a government that truly represents    the will of the people.

    India's democracy is characterized by its diversity, with multiple political parties representing various   ideologies, interests, and regions. Elections in India are marked by vigorous campaigns, political debates, and   enthusiastic participation by citizens. It is a celebration of the power of the people to shape their own     destiny.

    Overall, democracy in India stands as a symbol of the nation's commitment to pluralism, inclusivity, and the    principles of liberty and justice. It provides a platform for citizens to voice their opinions, choose their   leaders, and collectively strive towards a better and more prosperous future.''')

    # Elections
    st.header('Elections')
    st.markdown('''Elections in India hold immense significance and are pivotal moments in shaping the nation's     democratic fabric. With a population of over 1.3 billion people, India's elections are the largest democratic   exercise in the world. They serve as a platform for citizens to exercise their right to vote and actively     participate in the decision-making process.

    In India, elections are conducted regularly at the national, state, and local levels. They provide an   opportunity for citizens to choose their representatives who will govern and make decisions on their behalf.  Elections are marked by spirited campaigns, where political parties present their visions, policies, and     promises to the electorate.

    During election season, the air is filled with excitement, political rallies, and enthusiastic participation    from citizens. It is a time when the entire nation comes together to discuss and debate various issues, ranging    from governance and development to social welfare and national security.

    The Election Commission of India plays a pivotal role in ensuring the integrity of the electoral process. As an     independent constitutional body, it oversees the conduct of free and fair elections. The Commission ensures     that elections are conducted in a transparent manner, with equal opportunities for all candidates and strict    adherence to electoral guidelines.

    The process of elections in India is both complex and fascinating. Eligible citizens aged 18 and above have the     right to vote, and voter registration plays a crucial role in enabling them to exercise this right. The     Election Commission diligently works towards increasing voter awareness, promoting voter education, and     streamlining the voter registration process.

    On the day of elections, citizens across the country queue up at polling stations, waiting for their turn to    cast their vote. It is a powerful moment where every vote holds the potential to shape the nation's future. The    electoral process in India is conducted using electronic voting machines (EVMs) to ensure accuracy and     efficiency.

    Elections in India are not just about choosing leaders; they reflect the aspirations and dreams of millions of  citizens. They offer a chance for the common person to be heard, irrespective of their background or social  standing. Elections empower citizens to be active participants in the democratic process and hold their elected  representatives accountable for their actions.

    In India, elections are not merely events; they are celebrations of democracy and the power of the people. They     are a testament to India's commitment to the principles of inclusivity, diversity, and the collective will of   its citizens. Elections provide an opportunity for the nation to come together and collectively strive towards    a better, more prosperous future.

    Through the democratic process of elections, India continues to strengthen its democratic institutions, foster  citizen engagement, and uphold the values of liberty, equality, and justice. It is an ongoing journey towards    building a stronger and more vibrant democracy that truly represents the aspirations and aspirations of its    diverse population.''')

    # Voter Registration Benefits
    st.header('Voter Registration Benefits')
    st.markdown('Voter registration is essential for participating in elections. It offers several benefits,    including:')
    st.markdown('- Exercising your right to vote')
    st.markdown('- Having a say in the decision-making process')
    st.markdown('- Influencing policies and governance')
    st.markdown('- Holding elected officials accountable')

    # Footer
    st.info('Satyamev Jayate')


def main():
    # Initialize state variable
    page = st.session_state.get('page', 1)

    # Display Page 1 by default
    if page == 1:
        page1()
        # Add a "Next" button to navigate to Page 2
        if st.button("Next"):
            # Update state variable to go to Page 2
            st.session_state['page'] = 2

    # Display Page 2 if user navigates from Page 1
    elif page == 2:
        page2()
if __name__ == "__main__":
    main()
