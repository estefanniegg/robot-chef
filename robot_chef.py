#https://www.youtube.com/c/estefanniegg

import RPi.GPIO as GPIO
import unicornhathd
from PIL import Image, ImageDraw, ImageFont
import threading
import colorsys
from sys import exit
import time

from gpiozero import Servo
servo = Servo(17)

condition = threading.Condition()
GPIO.setmode(GPIO.BCM)

#motors
big_motor = 4

stepper = 27
stepper_dir = 22
stepper2 = 5
stepper2_dir = 6

GPIO.setup(big_motor, GPIO.OUT)
GPIO.setup(stepper, GPIO.OUT)
GPIO.setup(stepper_dir, GPIO.OUT)
GPIO.setup(stepper2, GPIO.OUT)
GPIO.setup(stepper2_dir, GPIO.OUT)


steps_to_stop = 7500
stepper_counter = 0
current_state = 0
chopping_time = 0
chopping_wait_time = 20

#Unicorn hat display stuff

#pngs
display_image = 0
INGREDIENT_IMAGE_BASE = 10
COUNTDOWN_IMAGE_BASE = 20
global drawing
unicornhathd.rotation(0)
unicornhathd.brightness(0.6)
width, height = unicornhathd.get_shape()

def display_thread():
	while True:
		condition.acquire()
		if display_image == 0:
			img = Image.open('go.png')
		elif display_image == 1:
			img = Image.open('done.png')
		elif display_image == 2:
			img = Image.open('cat.png')
# Ingredient images start at 10
		elif display_image == 10:
			img = Image.open('tomatoes.png')
		elif display_image == 11:
			img = Image.open('onions.png')
		elif display_image == 12:
			img = Image.open('serranos.png')
		elif display_image == 13:
			img = Image.open('cilantro.png')
		elif display_image == 14:
			img = Image.open('avocado.png')
		# COUNTDOWN 3
		elif display_image == 20:
			img = Image.open('three.png')
		elif display_image == 21:
			# COUNTDOWN 2
			img = Image.open('two.png')
		elif display_image == 22:
			# COUNTDOWN 1
			img = Image.open('one.png')

		for o_x in range(int(img.size[0] / width)):
	            	for o_y in range(int(img.size[1] / height)):
        	        	valid = False
                		for x in range(width):
                    			for y in range(height):
                      				pixel = img.getpixel(((o_x * width) + y, (o_y * height) + x))
     	                  			r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
                        			if r or g or b:
                           				valid = True
                      				unicornhathd.set_pixel(x, y, r, g, b)
                		if valid:
                    			unicornhathd.show()
    					time.sleep(0.5)
		condition.release()

def servo_thread():
	while True:
		servo.mid()
		time.sleep(0.5)
		servo.min()
		time.sleep(0.5)
		servo.mid()
		time.sleep(0.5)
		servo.min()
		time.sleep(0.5)


dt = threading.Thread(target=display_thread)
dt.start()
st = threading.Thread(target=servo_thread)
st.start()

#current_state
#display countdown of ingredient = 0
#chop_ingredient = 1
#sweep_tomatoes = 2
#bring knife back = 3
#infinite loop = 4

# always start at ingredient 0
current_ingredient = 0

try:
	while True:
		if current_state == 0:
			
                        display_image = INGREDIENT_IMAGE_BASE + current_ingredient
                        print('put ingredient #{}'.format(current_ingredient))
                        current_state = 1
			time.sleep(1.7)

			# Wait for next ingredient
			print('Coundown 3')
			display_image = COUNTDOWN_IMAGE_BASE + 0
			time.sleep(1.3)
			print('Coundown 2')
			display_image = COUNTDOWN_IMAGE_BASE + 1
			time.sleep(1.3)
			print('Coundown 1')
			display_image = COUNTDOWN_IMAGE_BASE + 2
			time.sleep(1.3)
			display_image = 0

			#display_image = INGREDIENT_IMAGE_BASE + current_ingredient
			#print('put ingredient #{}'.format(current_ingredient))
                        #current_state = 1
                        # time.sleep(4)

			# keep the image during cutting
			display_image = 10 + current_ingredient
		elif current_state == 1:
# display_image should stay the same and just animate
			drawing = True
			print('chopping - animals (ingredient #{})'.format(current_ingredient))
			GPIO.output(big_motor, True)
			time.sleep(4)
			print('chopping off')
			GPIO.output(big_motor, False)
			time.sleep(1)
			stepper_counter = 0
			current_ingredient = current_ingredient + 1
			if current_ingredient > 4:
# all 5 ingredients done. move to sweeping
				current_state = 2
			else:
				current_state = 0
		elif current_state == 2:
			if stepper_counter == steps_to_stop:
				print('done sweeping')
				current_state = 3
			else:
				display_image = 2
				GPIO.output(stepper_dir, GPIO.HIGH)
				GPIO.output(stepper2_dir, GPIO.HIGH)
				time.sleep(0.001)
				GPIO.output(stepper, GPIO.LOW)
				GPIO.output(stepper2, GPIO.LOW)
				print('moving giant knife - cat')
				time.sleep(0.001)
				GPIO.output(stepper, GPIO.HIGH)
				GPIO.output(stepper2, GPIO.HIGH)
				stepper_counter += 1
		elif current_state == 3:
			if stepper_counter == 0:
				print ('done going back, done')
				current_state = 4
			else:
				display_image = 2
				GPIO.output(stepper_dir, GPIO.LOW)
				GPIO.output(stepper2_dir, GPIO.LOW)
				time.sleep(0.001)
				GPIO.output(stepper, GPIO.LOW)
				GPIO.output(stepper2, GPIO.LOW)
				print('going back - avocado')
				time.sleep(0.001)
				GPIO.output(stepper, GPIO.HIGH)
				GPIO.output(stepper2, GPIO.HIGH)
				stepper_counter -=1
		elif current_state == 4:
			display_image = 1
			while True:
				pass

except KeyboardInterrupt:
	GPIO.cleanup()
	unicornhathd.off()
