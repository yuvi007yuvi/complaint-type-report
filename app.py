from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Global variable to store DataFrame
df = None

@app.route('/upload', methods=['POST'])
def upload_file():
    global df
    print("Received request to /upload")
    if 'file' not in request.files:
        print("No file part in request")
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        print("No selected file")
        return redirect(request.url)
    if file:
        print(f"File received: {file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        df = pd.read_csv(filepath)
        print("File processed and DataFrame updated")
        return redirect(url_for('index'))
    print("No file to process")

@app.route('/', methods=['GET', 'POST'])
def index():
    global df
    if df is None:
        # If no data is loaded, pass empty data to the template
        complaint_types = []
        complaint_subtypes = []
        grouped_complaints = {}
        complaint_counts = {}
        print("No CSV data loaded. Rendering index.html with empty data.")
    
    selected_type = request.form.get('complaint_type')
    selected_subtype = request.form.get('complaint_subtype')

    complaint_types = []
    complaint_subtypes = []
    grouped_complaints = {}
    complaint_counts = {}

    if df is not None:
        filtered_df = df
        if selected_type:
            filtered_df = filtered_df[filtered_df['Complainttype'] == selected_type]
        if selected_subtype:
            filtered_df = filtered_df[filtered_df['complaintsubtype'] == selected_subtype]

        complaint_types = df['Complainttype'].unique().tolist()
        complaint_subtypes = df['complaintsubtype'].unique().tolist()

        # Calculate complaint counts by type
        complaint_counts = filtered_df['Complainttype'].value_counts().to_dict()

        # Group complaints by type and then by subtype
        for complaint_type in filtered_df['Complainttype'].unique():
            grouped_complaints[complaint_type] = {}
            type_df = filtered_df[filtered_df['Complainttype'] == complaint_type]
            for complaint_subtype in type_df['complaintsubtype'].unique():
                subtype_df = type_df[type_df['complaintsubtype'] == complaint_subtype].copy()
                subtype_df['Sr No'] = range(1, len(subtype_df) + 1)
                grouped_complaints[complaint_type][complaint_subtype] = subtype_df.to_dict(orient='records')
        if selected_type:
            filtered_df = filtered_df[filtered_df['Complainttype'] == selected_type]
        if selected_subtype:
            filtered_df = filtered_df[filtered_df['complaintsubtype'] == selected_subtype]

        # Calculate complaint counts by type
        complaint_counts = filtered_df['Complainttype'].value_counts().to_dict()

        # Group complaints by type and then by subtype
        grouped_complaints = {}
        for complaint_type in filtered_df['Complainttype'].unique():
            grouped_complaints[complaint_type] = {}
            type_df = filtered_df[filtered_df['Complainttype'] == complaint_type]
            for complaint_subtype in type_df['complaintsubtype'].unique():
                subtype_df = type_df[type_df['complaintsubtype'] == complaint_subtype].copy()
                subtype_df['Sr No'] = range(1, len(subtype_df) + 1)
                grouped_complaints[complaint_type][complaint_subtype] = subtype_df.to_dict(orient='records')


    return render_template('index.html', 
                           complaint_types=complaint_types, 
                           complaint_subtypes=complaint_subtypes, 
                           grouped_complaints=grouped_complaints,
                           complaint_counts=complaint_counts,
                           selected_type=selected_type,
                           selected_subtype=selected_subtype)

if __name__ == '__main__':
    app.run(debug=True)