from flask import Flask, render_template, request, session
import os
import uuid
import pandas as pd
from werkzeug.utils import secure_filename

from ai_agent import ask_ai
from analysis import get_financial_analysis


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
    BASE_DIR,
    "static",
    "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Toegestane Excel-bestanden
ALLOWED_EXTENSIONS = {"xlsx", "xls"}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def get_financials(df):

    result = get_financial_analysis(df)

    # Als de analyse een dictionary teruggeeft
    if isinstance(result, dict):

        omzet = result["totale_omzet"]
        kosten = result["totale_kosten"]
        winst = result["totale_winst"]

    # Als de analyse een tuple of lijst teruggeeft
    else:

        omzet, kosten, winst = result

    return {
        "omzet": float(omzet),
        "kosten": float(kosten),
        "winst": float(winst)
    }


def format_euro(value):

    value = float(value)

    return (
        f"€ {value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


@app.route("/", methods=["GET", "POST"])
def home():

    message = ""
    financials = None
    filename = session.get("filename")

    # Excel upload
    if request.method == "POST" and "file" in request.files:

        file = request.files["file"]

        if not file or not file.filename:

            message = "Kies eerst een Excel-bestand."

        elif not allowed_file(file.filename):

            message = (
                "Alleen .xlsx en .xls bestanden zijn toegestaan."
            )

        else:

            original_name = secure_filename(
                file.filename
            )

            extension = original_name.rsplit(
                ".", 1
            )[1].lower()

            unique_name = (
                f"{uuid.uuid4().hex}.{extension}"
            )

            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                unique_name
            )

            file.save(file_path)

            try:

                # Excel lezen met Pandas
                df = pd.read_excel(file_path)

                # Bestand opslaan in session
                session["file_path"] = file_path
                session["filename"] = original_name

                filename = original_name

                # Financiële gegevens
                financials = get_financials(df)

                # Bedragen mooi formatteren
                financials["omzet"] = format_euro(
                    financials["omzet"]
                )

                financials["kosten"] = format_euro(
                    financials["kosten"]
                )

                financials["winst"] = format_euro(
                    financials["winst"]
                )

                message = (
                    f"'{original_name}' is succesvol "
                    "geüpload. Je kunt nu vragen "
                    "stellen over je data."
                )

            except Exception as e:

                message = (
                    f"Er ging iets mis met het "
                    f"Excel-bestand: {e}"
                )

    # Bestaand bestand opnieuw laden
    if filename and financials is None:

        file_path = session.get("file_path")

        if file_path and os.path.exists(file_path):

            try:

                df = pd.read_excel(file_path)

                financials = get_financials(df)

                financials["omzet"] = format_euro(
                    financials["omzet"]
                )

                financials["kosten"] = format_euro(
                    financials["kosten"]
                )

                financials["winst"] = format_euro(
                    financials["winst"]
                )

            except Exception:
                pass

    return render_template(
        "index.html",
        message=message,
        filename=filename,
        financials=financials
    )


@app.route("/ask", methods=["POST"])
def ask():

    file_path = session.get("file_path")

    if not file_path or not os.path.exists(file_path):

        return render_template(
            "index.html",
            message="Upload eerst een Excel-bestand."
        )

    question = request.form.get(
        "question",
        ""
    ).strip()

    if not question:

        return render_template(
            "index.html",
            message="Typ eerst een vraag."
        )

    try:

        # Excel opnieuw lezen
        df = pd.read_excel(file_path)

        # AI-agent gebruiken
        answer = ask_ai(
            question,
            df
        )

        # Financiële gegevens
        financials = get_financials(df)

        financials["omzet"] = format_euro(
            financials["omzet"]
        )

        financials["kosten"] = format_euro(
            financials["kosten"]
        )

        financials["winst"] = format_euro(
            financials["winst"]
        )

        return render_template(
            "index.html",
            filename=session.get("filename"),
            financials=financials,
            question=question,
            answer=answer
        )

    except Exception as e:

        return render_template(
            "index.html",
            filename=session.get("filename"),
            message=f"Er ging iets mis: {e}"
        )


if __name__ == "__main__":

    app.run(debug=True)