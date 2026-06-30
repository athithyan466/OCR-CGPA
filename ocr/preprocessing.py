"""
preprocessing.py
-----------------
Image preprocessing for semester-result screenshots before OCR.

Why each step exists (so you can tune it for your own screenshots):
- Grayscale: Tesseract works on single-channel intensity, color adds noise.
- Upscaling: phone/laptop screenshots are often <150 DPI effective; Tesseract
  is tuned for ~300 DPI scanned text, so we resize up.
- Denoising: screenshots compressed as JPG/PNG-from-screen-capture have
  artifacts around text edges that confuse character segmentation.
- Thresholding (binarization): converts to pure black/white, which is what
  Tesseract's internal algorithms expect for clean tables.
- Deskew: phone photos of a screen are rarely perfectly straight.
"""

import cv2
import numpy as np


class Preprocessor:
    """Cleans a raw result-screenshot image so OCR accuracy is maximized."""

    def __init__(self, scale_factor: float = 2.0, debug: bool = False):
        """
        Args:
            scale_factor: how much to upscale the image before OCR.
            debug: if True, intermediate steps are stored in self.debug_steps
                   so you can visualize them (useful in a Kaggle notebook).
        """
        self.scale_factor = scale_factor
        self.debug = debug
        self.debug_steps = {}

    def crop(self, img: np.ndarray, left: int = 0, top: int = 0,
              right: int = None, bottom: int = None) -> np.ndarray:
        """Crops out UI chrome (browser sidebars, scrollbars, app borders)
        that sit outside the actual result table and get OCR'd as garbage
        characters. Pass pixel coordinates measured on the ORIGINAL image
        (before upscale) — e.g. crop(img, left=40) to cut a left sidebar.
        """
        h, w = img.shape[:2]
        right = right if right is not None else w
        bottom = bottom if bottom is not None else h
        cropped = img[top:bottom, left:right]
        if self.debug:
            self.debug_steps["cropped"] = cropped.copy()
        return cropped

    def load(self, image_path: str) -> np.ndarray:
        """Load an image from disk as a BGR numpy array."""
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Could not read image at: {image_path}")
        if self.debug:
            self.debug_steps["original"] = img.copy()
        return img

    def to_grayscale(self, img: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if self.debug:
            self.debug_steps["grayscale"] = gray.copy()
        return gray

    def upscale(self, img: np.ndarray) -> np.ndarray:
        if self.scale_factor == 1.0:
            return img
        h, w = img.shape[:2]
        resized = cv2.resize(
            img,
            (int(w * self.scale_factor), int(h * self.scale_factor)),
            interpolation=cv2.INTER_CUBIC,
        )
        if self.debug:
            self.debug_steps["upscaled"] = resized.copy()
        return resized

    def denoise(self, img: np.ndarray) -> np.ndarray:
        denoised = cv2.fastNlMeansDenoising(img, h=10)
        if self.debug:
            self.debug_steps["denoised"] = denoised.copy()
        return denoised

    def deskew(self, img: np.ndarray) -> np.ndarray:
        """Corrects small rotations (common in photographed screenshots)."""
        coords = np.column_stack(np.where(img < 128))
        if coords.size == 0:
            return img
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        # Skip correction for near-zero or implausible angles (avoids
        # over-rotating already-straight digital screenshots).
        if abs(angle) < 0.5 or abs(angle) > 15:
            return img
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        if self.debug:
            self.debug_steps["deskewed"] = rotated.copy()
        return rotated

    def binarize(self, img: np.ndarray) -> np.ndarray:
        """Adaptive thresholding handles uneven lighting better than a global one."""
        thresh = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
        )
        if self.debug:
            self.debug_steps["binarized"] = thresh.copy()
        return thresh

    def sharpen(self, img: np.ndarray) -> np.ndarray:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(img, -1, kernel)
        if self.debug:
            self.debug_steps["sharpened"] = sharpened.copy()
        return sharpened

    def process(self, image_path: str, crop_box: tuple = None) -> np.ndarray:
        """Full pipeline: load -> (optional crop) -> grayscale -> upscale ->
        denoise -> deskew -> binarize.

        Args:
            image_path: path to the source image.
            crop_box: optional (left, top, right, bottom) in original-image
                      pixel coordinates, to remove sidebars/borders/scrollbars
                      that would otherwise get OCR'd as noise.

        Returns a single-channel (binary) numpy array ready for pytesseract.
        """
        img = self.load(image_path)
        if crop_box is not None:
            img = self.crop(img, *crop_box)
        gray = self.to_grayscale(img)
        gray = self.upscale(gray)
        gray = self.denoise(gray)
        gray = self.deskew(gray)
        final = self.binarize(gray)
        return final
