import os
import time
import threading
import tempfile
from seleniumwire import webdriver  # pip install selenium-wire
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import re
from time import sleep
import random
import json
import eel  # ← Thêm dòng này

class CookieGetter:
    def __init__(self, data):
        self.data = data

    def get_cookie(self, username, password, proxy=None):
        pass
    def thread_get_cookie(self):
        thread = threading.Thread(target=self.get_cookie, args=(self.data['username'], self.data['password'], self.data['proxy']))
        thread.start()