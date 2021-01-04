import time, datetime
import socket 
from board import SCL, SDA
import busio
import logging
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

# create a formatter that creates a single line of json with a comma at the end
formatter = logging.Formatter(("[%(asctime)s]:[%(levelname)s]:%(message)s"))

# create a channel for handling the logger and set its format
ch = logging.StreamHandler()
ch.setFormatter(formatter)

# connect the logger to the channel
ch.setLevel(logging.INFO)
logger.addHandler(ch)

class OledScreen:
    def __init__(self, width=128, height=32):
        self.width = width
        self.height = height

        self.font = ImageFont.load_default()
        self.padding = -2
        self.top = self.padding
        self.bottom = self.height - self.padding
        self.x = 0
        self.offset = 0

        self.init()
    
    def init(self):
        # Create the I2C interface
        i2c = busio.I2C(SCL, SDA)

        # Create the SSD1306 OLED class
        self.disp = adafruit_ssd1306.SSD1306_I2C(self.width, self.height, i2c)
        self.width = self.disp.width
        self.height = self.disp.height
        self.disp.fill(0)
        self.disp.show()

        # Create blank image for drawing
        # Make sure to create image with mode '1' for 1-bit color
        self.image = Image.new("1", (self.width, self.height))
        
        # Get drawing object to draw on image
        self.draw = ImageDraw.Draw(self.image)
        self.clear()
    
    @property
    def ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            logging.error(e)
            return '127.0.0.1'
    
    @property
    def hostname(self):
        try:
            return socket.gethostname()
        except Exception as e:
            logging.error(e)
            return 'Unknown'
    
    def clear(self):
        # clear the image
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
    
    def write(self, text, fill=255, reset_offset=False, offset=0):
        if reset_offset:
            self.offset = 0 # reset offset
        else:
            self.offset += 8 # global offset
            self.offset += offset # local offset

        self.draw.text((self.x, self.top + self.offset), text, font=self.font, fill=fill)

    def update(self):
        self.disp.image(self.image)
        self.disp.show()

    def show(self, interval=1):
        while True:
            try:
                self.clear()
                logger.info('updating oled screen')
                self.write('SmartCow', reset_offset=True)
                self.write('Fleet Management')
                self.write('IP: {}'.format(self.ip))
                self.write('HOST: {}'.format(self.hostname))
                self.update()
                time.sleep(interval)
            except Exception as e:
                logging.error(e)
                self.init()

OledScreen().show()