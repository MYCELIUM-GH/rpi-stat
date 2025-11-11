# ==== ==== ==== ==== ==== ==== ==== ====
# Small script to display Raspberry Pi system stats and Spotify track on SSD1306 display.
# ==== ==== ==== ==== ==== ==== ==== ====
# Made by MYCELIUM, 2025
# ==== ==== ==== ==== ==== ==== ==== ====
# ==== ==== IMPORTS ==== ====
# ==== ==== ==== ==== ==== ==== ==== ====
import os
import time
import subprocess
import psutil
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import spotipy
from spotipy.oauth2 import SpotifyOAuth
# ==== ==== ==== ==== ==== ==== ==== ====
# ==== ==== VARIABLES ==== ====
# ==== ==== ==== ==== ==== ==== ==== ====
OLED_WIDTH = 128
OLED_HEIGHT = 64
I2C_ADDRESS = 0x3C
# time in seconds for each display
DISPLAY_CYCLE_TIME = 5 
# requires SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI
# to be set as environment variables.
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-read-currently-playing user-read-playback-state" ))
# ==== ==== ==== ==== ==== ==== ==== ====
# ==== ==== I2C BUS CONF ==== ====
# ==== ==== ==== ==== ==== ==== ==== ====
try:
    i2c = busio.I2C(board.SCL, board.SDA)
except Exception as e:
    print(f"I2C setup failed. Error code: {e}")
    exit()
# ==== ==== ==== ==== ==== ==== ==== ====
# ==== ==== DISPLAY SETUP ==== ====
# ==== ==== ==== ==== ==== ==== ==== ====
try:
    oled = adafruit_ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=I2C_ADDRESS)
except Exception as e:
    print(f"OLED display setup failed. Error code: {e}")
    exit()
# reset display
oled.fill(0)
oled.show()
# ==== ==== ==== ==== ==== ==== ==== ====
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
# ==== ==== ==== ==== ==== ==== ==== ====
# ==== ==== FONT CONFIG ==== ====
# ==== ==== ==== ==== ==== ==== ==== ====
try:
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 10)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
    font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
except IOError:
    font_small = ImageFont.load_default()
    font = ImageFont.load_default()
    font_large = ImageFont.load_default()
# ==== ==== ==== ==== ==== ==== ==== ====
# ==== ==== MAIN FUNCTIONS ==== ====
# ==== ==== ==== ==== ==== ==== ==== ====
def get_cpu_temp():
    try:
        temp_output = subprocess.check_output(['vcgencmd', 'measure_temp']).decode('utf-8')
        return float(temp_output.split('=')[1].split('\'')[0])
    except:
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_raw = f.read()
                return int(temp_raw) / 1000.0
        except:
            return None
# ==== ==== ==== ==== ==== ==== ==== ====
def get_cpu_usage():
    return psutil.cpu_percent(interval=None)
# ==== ==== ==== ==== ==== ==== ==== ====
def get_ram_usage():
    ram = psutil.virtual_memory()
    total_mb = ram.total / (1024 * 1024 * 1024)
    used_mb = ram.used / (1024 * 1024 * 1024)
    percent = ram.percent
    return total_mb, used_mb, percent
# ==== ==== ==== ==== ==== ==== ==== ====
def get_disk_usage(path='/'):
    disk = psutil.disk_usage(path)
    total_gb = disk.total / (1024 * 1024 * 1024)
    used_gb = disk.used / (1024 * 1024 * 1024)
    percent = disk.percent
    return total_gb, used_gb, percent
# ==== ==== ==== ==== ==== ==== ==== ====
def get_network_speed():
    global prev_bytes_sent, prev_bytes_recv, last_net_time
    net_io = psutil.net_io_counters()
    current_bytes_sent = net_io.bytes_sent
    current_bytes_recv = net_io.bytes_recv
    current_time = time.time()
    upload_speed = 0
    download_speed = 0
    if last_net_time is not None and current_time - last_net_time > 0:
        time_diff = current_time - last_net_time
        upload_speed = (current_bytes_sent - prev_bytes_sent) / time_diff / 1024
        download_speed = (current_bytes_recv - prev_bytes_recv) / time_diff / 1024
    prev_bytes_sent = current_bytes_sent
    prev_bytes_recv = current_bytes_recv
    last_net_time = current_time
    return upload_speed, download_speed
# ==== ==== ==== ==== ==== ==== ==== ====
def get_current_track(spotify_client):
    try:
        current_playback = spotify_client.current_playback()
        if current_playback and current_playback['is_playing']:
            track = current_playback['item']['name']
            artist = ", ".join([a['name'] for a in current_playback['item']['artists']])
            return track, artist
        return None, None
    except Exception as e:
        print(f"Spotify error code: {e}")
        return None, None
# ==== ==== ==== ==== ==== ==== ==== ====
# ==== ==== NETWORK TRACKER ==== ====
# ==== ==== ==== ==== ==== ==== ==== ====
prev_bytes_sent = 0
prev_bytes_recv = 0
last_net_time = None
get_network_speed()
# ==== ==== ==== ==== ==== ==== ==== ====
# ==== ==== DISPLAY FUNCTIONS ==== ====
# ==== ==== ==== ==== ==== ==== ==== ====
def display_stats(draw, cpu_temp, cpu_usage, ram_used, ram_total, disk_used, disk_total, download_speed, upload_speed, font, font_large):
    draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), outline=0, fill=0)
    y_offset = 0
    # ==== ==== ==== ==== ==== ==== ==== ====
    # CPU
    if cpu_temp is not None:
        draw.text((0, y_offset), f"CPU {cpu_temp:.1f}°C/{cpu_usage:.1f}%", font=font_large, fill=255)
    else:
        draw.text((0, y_offset), "CPU Temp: N/A", font=font, fill=255)
    y_offset += 15
    # ==== ==== ==== ==== ==== ==== ==== ====
    # RAM
    draw.text((0, y_offset), f"RAM {ram_used:.1f}/{ram_total:.1f}GB", font=font_large, fill=255)
    y_offset += 15
    # ==== ==== ==== ==== ==== ==== ==== ====
    # ROM
    draw.text((0, y_offset), f"ROM {disk_used:.1f}/{disk_total:.1f}GB", font=font, fill=255)
    y_offset += 15
    # ==== ==== ==== ==== ==== ==== ==== ====
    # NETWORK
    draw.text((0, y_offset), f"NET {download_speed:.1f}D/{upload_speed:.1f}U KB/s", font=font, fill=255)
# ==== ==== ==== ==== ==== ==== ==== ====
def display_spotify(draw, track, artist, font_large, font_small):
    draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), outline=0, fill=0)
    # ==== ==== ==== ==== ==== ==== ==== ====
    if track and artist:
        draw.text((0, 0), "NOW PLAYING", font=font_large, fill=255)
        y_offset = 18
        draw.text((0, y_offset), track[:20], font=font_large, fill=255)
        # ==== ==== ==== ==== ==== ==== ==== ====
        y_offset += 18
        draw.text((0, y_offset), "Artist:", font=font_small, fill=255)
        y_offset += 12
        draw.text((0, y_offset), artist[:20], font=font_small, fill=255)
    else:
        draw.text((0, 0), "(No music)", font=font_large, fill=255)
# ==== ==== ==== ==== ==== ==== ==== ====
# ==== ==== MAIN LOOP ==== ====
# ==== ==== ==== ==== ==== ==== ==== ====
print("Ctrl+C to exit")
# 0 for stats, 1 for spotify
display_mode = 0 
# ==== ==== ==== ==== ==== ==== ==== ====
try:
    while True:
        # clear the image buffer
        draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
        # ==== ==== ==== ==== ==== ==== ==== ====
        if display_mode == 0:
            # ==== ==== ==== ==== ==== ==== ==== ====
            # display stats
            cpu_temp = get_cpu_temp()
            cpu_usage = get_cpu_usage()
            ram_total, ram_used, ram_percent = get_ram_usage()
            disk_total, disk_used, disk_percent = get_disk_usage()
            upload_speed, download_speed = get_network_speed()
            display_stats(draw, cpu_temp, cpu_usage, ram_used, ram_total, disk_used, disk_total, download_speed, upload_speed, font, font_large)
            # switch to spotify
            display_mode = 1
        # ==== ==== ==== ==== ==== ==== ==== ====
        elif display_mode == 1:
            # display spotify
            track, artist = get_current_track(sp)
            display_spotify(draw, track, artist, font_large, font_small)
            # switch back
            display_mode = 0
        # ==== ==== ==== ==== ==== ==== ==== ====
        # show output
        oled.image(image)
        oled.show()
        # ==== ==== ==== ==== ==== ==== ==== ====
        time.sleep(DISPLAY_CYCLE_TIME)
        # ==== ==== ==== ==== ==== ==== ==== ====
except KeyboardInterrupt:
    print("\nExiting the script")
finally:
    if 'oled' in locals():
        oled.fill(0)
        oled.show()
