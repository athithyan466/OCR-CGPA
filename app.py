from flask import Flask, render_template, request, jsonify
import os

from ocr.preprocessing import Preprocessor
from ocr.reader import Reader
from ocr.parser import GPAParser

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_image():

    try:
        print("STEP 1")

        image = request.files["image"]

        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)

        image.save(image_path)

        print("STEP 2") 

        preprocessor = Preprocessor()

        processed = preprocessor.process(image_path)

        print("STEP 3")

        import platform

        if platform.system() == "Windows":
            tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        else:
         tesseract_cmd = "tesseract"

        reader = Reader(tesseract_cmd=tesseract_cmd)

        print("STEP 4")

        raw_text = reader.read_text(processed)

        print("STEP 5")
        print(raw_text)

        parser = GPAParser()

        print("STEP 6")

        result = parser.parse(raw_text)

        print("STEP 7")
        print(result)

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)