import cv2
import numpy as np


class Preprocessor:

    def __init__(self, scale_factor=2.0):
        self.scale_factor = scale_factor

    def load(self, image_path):

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        return image

    def upscale(self, image):

        if self.scale_factor == 1:
            return image

        h, w = image.shape[:2]

        return cv2.resize(
            image,
            (int(w * self.scale_factor), int(h * self.scale_factor)),
            interpolation=cv2.INTER_CUBIC,
        )

    def denoise(self, image):

        return cv2.fastNlMeansDenoisingColored(
            image,
            None,
            10,
            10,
            7,
            21,
        )

    def sharpen(self, image):

        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])

        return cv2.filter2D(image, -1, kernel)

    def deskew(self, image):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        coords = np.column_stack(np.where(gray < 250))

        if len(coords) == 0:
            return image

        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        if abs(angle) < 0.5 or abs(angle) > 15:
            return image

        h, w = image.shape[:2]

        M = cv2.getRotationMatrix2D(
            (w // 2, h // 2),
            angle,
            1.0,
        )

        return cv2.warpAffine(
            image,
            M,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

    def process(self, image_path):

        image = self.load(image_path)

        image = self.upscale(image)

        image = self.denoise(image)

        image = self.sharpen(image)

        image = self.deskew(image)

        return image