"""
reader.py
---------
Thin wrapper around pytesseract/Tesseract that turns a preprocessed image
into raw text (and optionally structured word-level data with positions).
"""

import pytesseract
from pytesseract import Output
import numpy as np


class Reader:
    """Runs Tesseract OCR on a preprocessed image."""

    def __init__(self, lang: str = "eng", tesseract_cmd: str = None,
                 config: str = "--oem 3 --psm 4"):
        """
        Args:
            lang: Tesseract language code.
            tesseract_cmd: path to the tesseract binary, if it's not on PATH
                           (rarely needed on Kaggle, but configurable).
            config: Tesseract CLI flags.
                    --oem 3 = default LSTM engine.
                    --psm 4 = "assume a single column of text of variable
                    sizes", which works best for bordered result tables with
                    a title row above them. Try --psm 6 if your screenshot
                    has no borders/title and is just a plain text block.
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.lang = lang
        self.config = config

    def read_text(self, image: np.ndarray) -> str:
        """Return plain extracted text, preserving line breaks."""
        return pytesseract.image_to_string(image, lang=self.lang, config=self.config)

    def read_structured(self, image: np.ndarray) -> dict:
        """Return word-level OCR data (text, bounding boxes, confidence).

        Useful if you later want to reconstruct table rows/columns by their
        x/y coordinates instead of relying purely on text layout.
        """
        return pytesseract.image_to_data(
            image, lang=self.lang, config=self.config, output_type=Output.DICT
        )

    def average_confidence(self, structured_data: dict) -> float:
        """Mean confidence score (0-100) across recognized words, ignoring -1s."""
        confs = [int(c) for c in structured_data.get("conf", []) if str(c).strip() not in ("", "-1")]
        return sum(confs) / len(confs) if confs else 0.0