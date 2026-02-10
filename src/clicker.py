import pyautogui
import time
from typing import Optional
from .config import Config


class Clicker:
    def __init__(self, config: Config):
        self.config = config.click
        self.click_type = self.config.get('click_type', 'single')
        self.interval = self.config.get('interval', 1.0)
        self.offset_x = self.config.get('offset_x', 0)
        self.offset_y = self.config.get('offset_y', 0)

    def click(self, x: int, y: int, click_type: str = None):
        target_x = x + self.offset_x
        target_y = y + self.offset_y
        click_type = click_type or self.click_type

        pyautogui.moveTo(target_x, target_y, duration=0.2)

        if click_type == 'single':
            pyautogui.click()
        elif click_type == 'double':
            pyautogui.doubleClick()
        elif click_type == 'right':
            pyautogui.rightClick()
        else:
            pyautogui.click()

        time.sleep(self.interval)

    def click_with_retry(self, x: int, y: int, target_text: str = None,
                         max_retries: int = 3, retry_interval: float = 1.0):
        for attempt in range(max_retries):
            try:
                self.click(x, y)
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
                else:
                    raise e
        return False

    def get_screen_size(self):
        return pyautogui.size()

    def is_point_on_screen(self, x: int, y: int) -> bool:
        screen_size = self.get_screen_size()
        return 0 <= x < screen_size.width and 0 <= y < screen_size.height
