import pytesseract
from PIL import Image
from typing import List, Tuple, Optional
import mss
import mss.tools
import io


class ScreenOCR:
    def __init__(self, config):
        self.config = config
        self.confidence = config.ocr.get('confidence', 0.8)
        self.language = config.ocr.get('language', 'chi_sim')
        self.region = config.ocr.get('region')

    def capture_screen(self) -> Image.Image:
        with mss.mss() as sct:
            if self.region:
                monitor = {
                    'left': self.region[0],
                    'top': self.region[1],
                    'width': self.region[2],
                    'height': self.region[3]
                }
            else:
                monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            return Image.frombytes('RGB', screenshot.size, screenshot.rgb)

    def find_text(self, target_text: str) -> Optional[Tuple[int, int, int, int]]:
        screenshot = self.capture_screen()
        text_positions = self.find_all_text(target_text)
        if text_positions:
            return text_positions[0]
        return None

    def find_all_text(self, target_text: str) -> List[Tuple[int, int, int, int]]:
        screenshot = self.capture_screen()
        screenshot_path = 'temp_screenshot.png'
        screenshot.save(screenshot_path)

        data = pytesseract.image_to_data(
            Image.open(screenshot_path),
            lang=self.language,
            output_type=pytesseract.Output.DICT
        )

        positions = []
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            text = data['text'][i].strip()
            if target_text in text:
                confidence = float(data['conf'][i]) / 100
                if confidence >= self.confidence:
                    x = int(data['left'][i])
                    y = int(data['top'][i])
                    w = int(data['width'][i])
                    h = int(data['height'][i])
                    positions.append((x, y, x + w, y + h))

        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

        return positions

    def get_text_position(self, target_text: str) -> Optional[Tuple[int, int]]:
        result = self.find_text(target_text)
        if result:
            x1, y1, x2, y2 = result
            return (x1 + (x2 - x1) // 2, y1 + (y2 - y1) // 2)
        return None

    def recognize_all_text(self) -> str:
        screenshot = self.capture_screen()
        return pytesseract.image_to_string(screenshot, lang=self.language)
