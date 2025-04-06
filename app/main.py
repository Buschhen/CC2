from flask import Flask, request, render_template, send_file
import socket
import os
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from dotenv import load_dotenv
from pdf_summarizer import summarize_pdf

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

        if uploaded_file.filename.endswith('.pdf'):
            try:
                pdf_data = uploaded_file.read()
                summary = summarize_pdf(pdf_data)

                # Upload PDF
                pdf_blob = container_client.get_blob_client(uploaded_file.filename)
                pdf_blob.upload_blob(BytesIO(pdf_data), overwrite=True)

                # Save summary as a .summary.txt blob
                summary_blob_name = uploaded_file.filename + ".summary.txt"
                summary_blob = container_client.get_blob_client(summary_blob_name)
                summary_blob.upload_blob(summary, overwrite=True)





                # Upload the PDF file
                # pdf_blob.upload_blob(BytesIO(pdf_data), overwrite=True)
                # summary = summarize_pdf(pdf_data)
                message = f"✅ Uploaded PDF and note: {uploaded_file.filename}"

            except Exception as e:
                message = f"❌ Upload failed: {e}"

        else:
            message = "❗ Please upload a valid PDF file."

    # List only PDF files (filtering out .note.txt files)
    blobs = container_client.list_blobs()
    blob_list = [blob.name for blob in blobs if not blob.name.endswith(".note.txt")]

    return render_template(
        "index.html",
        hostname=hostname,
        message=message,
        blob_list=blob_list,
        summary=summary if 'summary' in locals() else None
    )


@app.route('/download/<filename>')
def download_file(filename):
    try:
        blob_client = container_client.get_blob_client(filename)
        stream = blob_client.download_blob().readall()
        return send_file(BytesIO(stream), download_name=filename, as_attachment=True)
    except Exception as e:
        return f"Error downloading file: {e}", 500
    
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    try:
        # Delete PDF
        blob_client = container_client.get_blob_client(filename)
        blob_client.delete_blob()

        # Also delete the associated note, if it exists
        note_blob_name = filename + ".note.txt"
        note_blob = container_client.get_blob_client(note_blob_name)
        if note_blob.exists():
            note_blob.delete_blob()

        return "Deleted", 204
    except Exception as e:
        return f"Error deleting file: {e}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
