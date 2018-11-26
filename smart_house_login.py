import serial
import time
import msvcrt

def timeout_input(prompt_text, timeout = 5):
    print(prompt_text)

    # Define end time.
    finish_time = time.time() + timeout

    # Input from keyboard.
    input_text = []
    while True:
        if msvcrt.kbhit():
            ch = msvcrt.getche().decode('utf-8')
            # End if 'enter' is pressed.
            if ch == '\r':
                return ''.join(input_text)
            else:
            	input_text.append(ch)

            time.sleep(0.1)          
        else:
            # Check if defined time passed.
            if time.time() > finish_time:
                return None

try:
    password = 'pms'
    serPort = serial.Serial('COM27', 9600)
	
    for attempt_num in range(3):
        passw = timeout_input('Password: ')
        if(passw == None):
            print('You did not enter password!')
        else:
            print(passw)

        if(passw == None): # Time passed.
            serPort.write(b'0')
            print('15 sec passed. '
            	  'You cannot enter the smart house.')
            break
        elif (passw == password): # The password is correct.
            serPort.write(b'1')
            print('You entered smart house.')
            break
        elif (attempt_num == 2): # Wrong password 3 times.
            serPort.write(b'0')
            print('Wrong password for the 3rd time. '
            	  'You cannot enter the smart house.')
            break
        else: # Wrong password 1 or 2 times.
            print('Wrong password. Try again.')

    print('Closing port...')
    serPort.close()
except KeyboardInterrupt:
    print('Closing port...')
    serPort.close()