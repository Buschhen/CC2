from flask import Flask, request, render_template, send_file, session, redirect, url_for
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from io import BytesIO
import os
import socket

from pdf_summarizer import summarize_pdf

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-key")

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

                pdf_data = uploaded_file.read()
                file_size = len(pdf_data)


                pdf_blob = container_client.get_blob_client(uploaded_file.filename)
                pdf_blob.upload_blob(BytesIO(pdf_data), overwrite=True)


                summary_key = f"{uploaded_file.filename}.{file_size}.summary.txt"
                summary_blob = container_client.get_blob_client(summary_key)

                # Check if summary already exists
                if summary_blob.exists():
                    session["summary"] = summary_blob.download_blob().readall().decode("utf-8")
                    session["message"] = f"✅ Reused cached summary for: {uploaded_file.filename}"
                else:
                    summary = summarize_pdf(pdf_data)
                    summary_blob.upload_blob(summary, overwrite=True)
                    session["message"] = f"✅ Uploaded and summarized: {uploaded_file.filename}"

            except Exception as e:
                session["message"] = f"❌ Upload failed: {e}"
        else:
            session["message"] = "❗ Please upload a valid PDF file."


        return redirect(url_for("upload"))


    blobs = list(container_client.list_blobs())

    pdfs = []

    for blob in blobs:
        if blob.name.endswith(".pdf"):
            matching_summaries = [
                b.name for b in blobs
                if b.name.startswith(blob.name + ".") and b.name.endswith(".summary.txt")
            ]
            summary_text = "❌ No summary available"

            if matching_summaries:
                summary_blob = container_client.get_blob_client(matching_summaries[0])
                summary_text = summary_blob.download_blob().readall().decode("utf-8")

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
        pdf_blob = container_client.get_blob_client(filename)
        pdf_blob.delete_blob()

        summary_blob = container_client.get_blob_client(filename + ".summary.txt")
        if summary_blob.exists():
            summary_blob.delete_blob()

        return "Deleted", 204
    except Exception as e:
        return f"Error deleting file: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
