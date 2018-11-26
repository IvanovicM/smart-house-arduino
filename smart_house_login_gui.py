import time
import serial
import queue
from threading import Thread
from tkinter import *

PASSWORD = 'pms'
LOGIN_NUM = 3

def login_handler(pass_entry, info, q):    
    # Check if the entered password is correct.
    text = pass_entry.get()
    if text == PASSWORD:
        # Inform other threads that user tried to log in.
        q.put(True)
        info.set('You entered the smart house.')
    else:
    	# Inform other threads that user tried to log in.
        q.put(False)
        info.set('Wrong password.')

def create_window():
    window = Tk()
    window.title('Smart House Login')

    info = StringVar()
    info_label = Label(window, textvariable=info)
    info.set('Welcome to Smart House!')
    info_label.pack()

    frame = Frame(window)
    pass_label = Label(frame, text='Enter password')
    pass_label.pack(side=LEFT)
    pass_entry = Entry(frame, width=50)
    pass_entry.pack(side=LEFT)
    frame.pack()

    login_button = Button(window, text='Login',
        command= lambda: login_handler(pass_entry, info, q))
    login_button.pack()

    window.mainloop()

def wait_to_login(timeout=5):
    end_time = time.time() + timeout
    
    login_pressed = False
    logged = False
    if not q.empty():
        login_pressed = True
        logged = q.get()

    global all_threads_alive
    while not login_pressed:
        if not q.empty():
            login_pressed = True
            logged = q.get()

        time.sleep(0.1)
        if time.time() >= end_time:
            break

    # Write to serial port.
    global serPort
    if login_pressed and logged:
    	serPort.write(b'1')
    if (not login_pressed) or (login_pressed and attempt_num == 3):
    	serPort.write(b'0')

    # Check if user tried to log in and is logged in.
    # Senf information to serial port.
    global run_login
    global login_tried
    if login_pressed:
    	login_tried = True
    	if logged:
    		run_login = False
    	elif attempt_num == 3:
    		logged = False

# Open serial port
serPort = serial.Serial('COM27', 9600)

# Queue for data sharing between threads.
q = queue.Queue()

# Create thread for login window.
login_view_thread = Thread(target=create_window)
login_view_thread.start()

# Try to login LOGIN_NUM times.
run_login = True
attempt_num = 0
login_tried = False
all_threads_alive = True
while run_login and attempt_num < LOGIN_NUM:    
    attempt_num = attempt_num + 1
    
    # Create timeout thread.   
    login_tried = False
    timeout_thread = Thread(target=wait_to_login)
    timeout_thread.start()

    all_threads_alive = True
    while all_threads_alive:
	    # Check if 15 seconds passed.
        if not timeout_thread.isAlive():
            if not login_tried:
                print('15 seconds passed.')
                run_login = False
            all_threads_alive = False

        # Check if the login window is closed.
        if not login_view_thread.isAlive():
            print('Login window is closed.')
            all_threads_alive = False
            run_login = False

        # Sleep for some time and then check again.
        time.sleep(0.1)

# Release resources.
print('Close port...')
serPort.close()