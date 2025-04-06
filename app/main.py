from flask import Flask, request, render_template_string, send_file
import socket
import os
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from dotenv import load_dotenv

# === Load environment variables from .env ===
load_dotenv()

app = Flask(__name__)

# === Azure Blob Config ===
AZURE_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("STORAGE_CONTAINER_NAME", "documents")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

@app.route('/', methods=['GET', 'POST'])
def upload():
    hostname = socket.gethostname()
    message = ''

    if request.method == 'POST':
        uploaded_file = request.files['pdf']
        note = request.form['note']

        if uploaded_file.filename.endswith('.pdf'):
            try:
                # Upload the PDF file
                pdf_blob = container_client.get_blob_client(uploaded_file.filename)
                pdf_blob.upload_blob(uploaded_file.stream, overwrite=True)

                # Upload the note as a .txt file
                note_blob_name = uploaded_file.filename + ".note.txt"
                note_blob = container_client.get_blob_client(note_blob_name)
                note_blob.upload_blob(note, overwrite=True)

                message = f"✅ Uploaded PDF and note: {uploaded_file.filename}"

            except Exception as e:
                message = f"❌ Upload failed: {e}"

        else:
            message = "❗ Please upload a valid PDF file."

    # List only PDF files (filtering out .note.txt files)
    blobs = container_client.list_blobs()
    blob_list = [blob.name for blob in blobs if not blob.name.endswith(".note.txt")]

    return render_template_string("""
        <h2>Upload a PDF and a note ({{ hostname }})</h2>
        <form method="post" enctype="multipart/form-data">
            <label>PDF File:</label><br>
            <input type="file" name="pdf" required><br><br>
            <label>Note:</label><br>
            <input type="text" name="note" required><br><br>
            <input type="submit" value="Upload">
        </form>
        <p>{{ message }}</p>

        <h3>📁 Uploaded PDFs</h3>
        <ul>
        {% for file in blob_list %}
            <li><a href="/download/{{ file }}">{{ file }}</a></li>
        {% endfor %}
        </ul>
    """, hostname=hostname, message=message, blob_list=blob_list)

@app.route('/download/<filename>')
def download_file(filename):
    try:
        blob_client = container_client.get_blob_client(filename)
        stream = blob_client.download_blob().readall()
        return send_file(BytesIO(stream), download_name=filename, as_attachment=True)
    except Exception as e:
        return f"Error downloading file: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
