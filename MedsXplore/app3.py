import os
import csv
from flask import Flask, render_template, request, redirect, flash, send_from_directory
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import pandas as pd
from googletrans import Translator
import pyttsx3
import json
def read_config(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config
config_file = 'config.txt'
config = read_config(config_file)
subscription_key = config['subscription_key']
endpoint = config['endpoint']
credentials = CognitiveServicesCredentials(subscription_key)
client = ComputerVisionClient(endpoint, credentials)
app = Flask(__name__)
# Configure a secret key for the session
secret_key = config.get('SECRET_KEY')
app.config['SECRET_KEY'] = 'secret_key'
# Define the upload folder for images
app.config['UPLOAD_FOLDER'] = 'uploads'
# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            # Save the uploaded file
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
            file.save(image_path)
            # Perform OCR on the uploaded image
            with open(image_path, "rb") as image_file:
                result = client.recognize_printed_text_in_stream(image_file)
            # Extract and print the recognized text
            recognized_text = []
            for region in result.regions:
                for line in region.lines:
                    for word in line.words:
                        recognized_text.append(word.text)
            # Load your dataset from a CSV file
            df = pd.read_csv('Medicine_Details.csv')
            # Initialize a dictionary to store matched rows with all columns
            matched_rows = {}
            # Initialize a dictionary to store matched rows with the first 6 letters
            matched_rows_with_first_6_letters = {}
            # Iterate through the dataset and check for an exact case-insensitive match
            selected_language = request.form.get('language')
            # Create a Translator instance
            translator = Translator()
            # Iterate through the dataset and check for a match
            for index, row in df.iterrows():
                medicine_value = str(row['Medicine']).lower()
                for ocr_word in recognized_text:
                    if ocr_word.lower() == medicine_value:
                        if medicine_value not in matched_rows:
                            matched_rows[medicine_value] = []
                        matched_rows[medicine_value].append(row.to_dict())
            if not matched_rows:
                matched_rows_with_first_6_letters = {}
                for index, row in df.iterrows():
                    medicine_value = row['Medicine'][:6].lower()

                    for ocr_word in recognized_text:
                        if ocr_word.lower().startswith(medicine_value):
                            if medicine_value not in matched_rows_with_first_6_letters:
                                matched_rows_with_first_6_letters[medicine_value] = []
                            matched_rows_with_first_6_letters[medicine_value].append(row.to_dict())
            # If there are exact matches, use them; otherwise, use matches based on the first 6 letters
            final_matched_rows = matched_rows if matched_rows else matched_rows_with_first_6_letters
            # Translate the "Uses" and "Side Effects" columns
            translated_matched_rows = {}
            for medicine_value, rows in final_matched_rows.items():
                translated_rows = []
                for row in rows:
                    translated_row = row.copy()
                    if 'Uses' in row:
                        # Translate the "Uses" column to the selected language
                        try:
                            translated_uses = translator.translate(row['Uses'], dest=selected_language).text
                            translated_row['Uses'] = translated_uses
                        except Exception as e:
                            translated_row['Uses'] = "Translation Error"
                    if 'Side_effects' in row:
                        # Translate the "Side Effects" column to the selected language
                        try:
                            translated_side_effects = translator.translate(row['Side_effects'], dest=selected_language).text
                            translated_row['Side_effects'] = translated_side_effects
                        except Exception as e:
                            translated_row['Side_effects'] = "Translation Error"
                    if 'Medicine' in row:
                        # Translate the "Side Effects" column to the selected language
                        try:
                            translated_side_effects = translator.translate(row['Medicine'], dest=selected_language).text
                            translated_row['Medicine'] = translated_side_effects
                        except Exception as e:
                            translated_row['Medicine'] = "Translation Error"
                    translated_rows.append(translated_row)
                translated_matched_rows[medicine_value] = translated_rows           
            return render_template('index.html', ocr_result=recognized_text, matched_rows=translated_matched_rows, selected_language=selected_language,row=row)
    return render_template('index.html')
app.config['COMPLAINTS_FOLDER'] = 'static/complaints'
os.makedirs(app.config['COMPLAINTS_FOLDER'], exist_ok=True)
@app.route('/register_complaint', methods=['GET', 'POST'])
def register_complaint():
    if request.method == 'POST':
        # Get the medicine name and image file from the form
        medicine_name = request.form.get('medicine_name')
        file = request.files['file']
        # Save the uploaded file
        complaint_image_path = os.path.join(app.config['COMPLAINTS_FOLDER'], f'{medicine_name}_complaint.jpg')
        file.save(complaint_image_path)
        # You can add additional logic to store the complaint information in a database or file
        # For simplicity, let's just print the details
        print(f"Complaint Registered: Medicine Name - {medicine_name}, Image Path - {complaint_image_path}")
        flash('Complaint registered successfully! We will look into it.')
        return redirect(request.url)
    return render_template('register_complaint.html')
@app.route('/admin/complaints', methods=['GET'])
def view_complaints():
    # Get the list of complaint files in the complaints folder
    complaint_files = os.listdir(app.config['COMPLAINTS_FOLDER'])
    complaints = []
    for file_name in complaint_files:
        if file_name.endswith('_complaint.jpg'):
            medicine_name = file_name.split('_complaint.jpg')[0]
            image_path = os.path.join(app.config['COMPLAINTS_FOLDER'], file_name)
            complaints.append({'medicine_name': medicine_name, 'image_path': image_path})
    return render_template('admin_complaints.html', complaints=complaints)
csv_file = 'Medicine_Details.csv'
@app.route('/update_data', methods=['POST'])
def update_data():
    medicine = request.form.get('medicine')
    composition = request.form.get('composition')
    uses = request.form.get('uses')
    side_effects = request.form.get('side_effects')
    image = request.form.get('image')
    manufacturer = request.form.get('manufacturer')
    excellent_review = request.form.get('excellent_Review')
    average_review = request.form.get('average_review')
    poor_review = request.form.get('poor_review')
    # Write new data to the CSV file
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([medicine, composition, uses, side_effects, image, manufacturer, excellent_review, average_review, poor_review])
    return 'Data updated successfully!'
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
pharmacy_base_url = 'https://pharmeasy.in/search/all?name='
@app.route('/buy_now/<medicine_name>')
def buy_now(medicine_name):
    # Construct the complete URL by appending the medicine name as a parameter
    pharmacy_url = pharmacy_base_url + medicine_name
    # Redirect the user to the pharmacy website with the specific medicine name
    return redirect(pharmacy_url)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

