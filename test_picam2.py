from picamera2 import Picamera2
import numpy as np

def capture_from_picam():
    picam2 = Picamera2()
    
    # Configure the camera
    picam2.start_preview()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.configure(picam2.preview_configuration)

    # Capture an image
    picam2.start()
    image = picam2.capture_array()
    picam2.stop()

    # Convert the captured image to a format suitable for saving
    # This example converts it to a PIL Image, but you can adjust it as needed
    from PIL import Image
    captured_image = Image.fromarray(np.uint8(image)).convert('RGB')

    return captured_image


image = capture_from_picam()
image.save('picam_output.png')
