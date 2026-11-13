
from flask import Flask, render_template, request, session
import os
import uuid
import pandas as pd
from werkzeug.utils import secure_filename

from ai_agent import ask_ai
from analysis import get_dataset_info


# Project root
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "excelinsight-development-key"


# Upload folder
UPLOAD_FOLDER = os.path.join(
    BASE_DIR, "static", "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"xlsx", "xls"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# Algemene Excel-informatie ophalen
def load_excel(file_path):
    df = pd.read_excel(file_path)

    if df.empty:
        raise ValueError(
            "Het Excel-bestand bevat geen gegevens."
        )

    return df, get_dataset_info(df)


# Dashboard
@app.route("/", methods=["GET", "POST"])
def home():

    message = ""
    dataset_info = None
    financials = None

    filename = session.get("filename")
    file_path = session.get("file_path")

    # Nieuw Excel-bestand uploaden
    if request.method == "POST" and "file" in request.files:

        file = request.files["file"]

        if not file or not file.filename:
            message = "Kies eerst een Excel-bestand."

        elif not allowed_file(file.filename):
            message = (
                "Alleen .xlsx en .xls bestanden zijn toegestaan."
            )

        else:
            original_name = secure_filename(file.filename)
            extension = original_name.rsplit(".", 1)[1].lower()

            unique_name = f"{uuid.uuid4().hex}.{extension}"

            new_file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                unique_name
            )

            file.save(new_file_path)

            try:
                df, dataset_info = load_excel(new_file_path)

                session["file_path"] = new_file_path
                session["filename"] = original_name

                filename = original_name
                file_path = new_file_path

                message = (
                    f"'{original_name}' is succesvol geüpload. "
                    "Je kunt nu vragen stellen over je data."
                )

            except Exception as e:
                os.remove(new_file_path)
                message = f"Er ging iets mis: {e}"

    # Bestaand Excel-bestand opnieuw laden
    if dataset_info is None and file_path:

        if os.path.exists(file_path):
            try:
                df, dataset_info = load_excel(file_path)

            except Exception as e:
                message = f"Er ging iets mis: {e}"

    return render_template(
        "index.html",
        message=message,
        filename=filename,
        financials=financials,
        dataset_info=dataset_info
    )


# AI-vragen
@app.route("/ask", methods=["POST"])
def ask():

    file_path = session.get("file_path")
    filename = session.get("filename")

    if not file_path or not os.path.exists(file_path):
        return render_template(
            "index.html",
            message="Upload eerst een Excel-bestand."
        )

    question = request.form.get(
        "question", ""
    ).strip()

    if not question:
        return render_template(
            "index.html",
            message="Typ eerst een vraag.",
            filename=filename
        )

    try:
        # Excel lezen
        df, dataset_info = load_excel(file_path)

        # AI-agent gebruiken
        answer = ask_ai(question, df)

        return render_template(
            "index.html",
            filename=filename,
            financials=None,
            dataset_info=dataset_info,
            question=question,
            answer=answer
        )

    except Exception as e:
        return render_template(
            "index.html",
            filename=filename,
            financials=None,
            message=f"Er ging iets mis: {e}"
        )


if __name__ == "__main__":
    app.run(debug=True)
