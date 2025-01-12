from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui as pg
import time

# Set up the Chrome WebDriver
chrome_options = Options()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# variables containing the app canvas position and distance to the browser's content area
canvas_pos = None
panel_height = 0

# Navigate to the Dinosaur Game and start game
driver.get("https://www.google.com")
driver.set_network_conditions(offline=True, latency=5, throughput=500 * 1024)
pg.alert(text='Press "esc" followed by "ctrl+C" to stop the game', title='Stop Game', button='OK')
pg.FAILSAFE = False # avoids unwanted loop interruptions due to mouse moving outside screen


try:
    driver.get("https://www.google.com")
    
except:
    pass

# maximize window to obtain absolute screen coordinates
driver.fullscreen_window()
time.sleep(1)

panel_height = int(driver.execute_script('return window.outerHeight - window.innerHeight;'))

# # Press the space key to start the game
pg.press('space')
time.sleep(1)

# dinamically define regions for background and obstacle samples
canvas_found = False
while not canvas_found:
    try:
        canvas = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.runner-container canvas.runner-canvas")))
        canvas_pos = canvas.rect  # Returns a dictionary with  'height', 'width', 'x', and 'y'
        # define absolute screenshot coords. Dino is between 22 and 50 pixels from the left side of canvas
        top_left_x = (int(canvas_pos['x']) + 5)  
        top_left_y = int(canvas_pos['y'] + panel_height)
        bottom_right_x = int(canvas_pos['x'] + canvas_pos['width'] / 4) # approximately 150 pxls
        bottom_right_y = int(canvas_pos['y'] + panel_height + canvas_pos['height'] * 4 / 5) # approximately 120 pxs
        canvas_found = True
    except Exception as e:
        print(f"Exception: {e}")
        pass

# converts screenshot diagonal coordsa into bbox format
region = (top_left_x, 
          top_left_y, 
          bottom_right_x - top_left_x, 
          bottom_right_y - top_left_y) 
game_on = True
while game_on:  
    start_time = time.time() 
    canvas_img = pg.screenshot(region=region)
    canvas_img.save('canvas.png')
    # converts image to b&w
    gray_img = canvas_img.convert('L')
    bw_img = gray_img.point(lambda i: 255 if i > 128 else 0)
    bw_img.save("bw.png")
    # compare sthe value of a pixel in the top-leftt backgronud with a line of pixels at bottom-right. Adjust coordinates from absolute to relative
    bg_pixel_value = bw_img.getpixel((5, 5))
    obst_line = bw_img.crop((bottom_right_x - top_left_x - 81, # this is approximately 20 pixels ahead of Dino
                             bottom_right_y - top_left_y - 2, # this is approximately at Dino's waist
                             bottom_right_x - top_left_x - 51, 
                             bottom_right_y - top_left_y - 1))    
    obstacle_pixels = set(obst_line.getdata())
    if bg_pixel_value not in obstacle_pixels or len(obstacle_pixels) > 1:
        pg.press('space')
        print("Jumping")
    else:
        pass
    # End measuring time  
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"While loop completed in {elapsed_time:.6f} seconds")
  
# Close the browser
driver.quit()
