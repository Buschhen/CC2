from flask import Flask, request, render_template, send_file, session, redirect, url_for
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from io import BytesIO
import os
import socket

from pdf_summarizer import summarize_pdf  # Your updated summarizer

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key")

# Azure config
AZURE_CONNECTION_STRING = os.getenv("AZURE_BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("STORAGE_CONTAINER_NAME", "documents")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)

@app.route("/", methods=["GET", "POST"])
def upload():
    hostname = socket.gethostname()
    message = session.pop("message", "")
    summary = session.pop("summary", None)

    if request.method == "POST":
        uploaded_file = request.files["pdf"]

        if uploaded_file.filename.endswith(".pdf"):
            try:
                # Read file once into memory
                pdf_data = uploaded_file.read()

                # Upload PDF
                pdf_blob = container_client.get_blob_client(uploaded_file.filename)
                pdf_blob.upload_blob(BytesIO(pdf_data), overwrite=True)

                # Summarize
                summary = summarize_pdf(pdf_data)

                # Upload summary
                summary_blob = container_client.get_blob_client(uploaded_file.filename + ".summary.txt")
                summary_blob.upload_blob(summary, overwrite=True)

                session["message"] = f"✅ Uploaded PDF and summary: {uploaded_file.filename}"
                session["summary"] = summary

            except Exception as e:
                session["message"] = f"❌ Upload failed: {e}"
        else:
            session["message"] = "❗ Please upload a valid PDF file."

        return redirect(url_for("upload"))  # 🔁 Prevent form re-submission

    # Prepare list of PDFs with summaries
    blobs = list(container_client.list_blobs())
    pdfs = []

    for blob in blobs:
        if blob.name.endswith(".pdf"):
            summary_blob_name = blob.name + ".summary.txt"
            summary_text = "❌ No summary available"

            try:
                summary_blob = container_client.get_blob_client(summary_blob_name)
                if summary_blob.exists():
                    summary_text = summary_blob.download_blob().readall().decode("utf-8")
            except:
                pass

            pdfs.append({
                "filename": blob.name,
                "summary": summary_text
            })

    return render_template(
        "index.html",
        hostname=hostname,
        message=message,
        summary=summary,
        pdfs=pdfs
    )


@app.route("/download/<filename>")
def download_file(filename):
    try:
        blob_client = container_client.get_blob_client(filename)
        stream = blob_client.download_blob().readall()
        return send_file(BytesIO(stream), download_name=filename, as_attachment=True)
    except Exception as e:
        return f"Error downloading file: {e}", 500


@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    try:
        # Delete PDF
        pdf_blob = container_client.get_blob_client(filename)
        pdf_blob.delete_blob()

        # Delete associated summary
        summary_blob = container_client.get_blob_client(filename + ".summary.txt")
        if summary_blob.exists():
            summary_blob.delete_blob()

        return "Deleted", 204
    except Exception as e:
        return f"Error deleting file: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
