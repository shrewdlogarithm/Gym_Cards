try: # these are the Pi only card reads - they will fail on desktop

    ## This is the later code for the RC522
    # import RPi.GPIO as GPIO
    # GPIO.setmode(GPIO.BOARD)
    # GPIO.setwarnings(False)
    # GPIO.setup(11, GPIO.OUT)	
    # from RC522_Python import RFID
    # rdr = RFID()
    # def readpi():
    #     cn = 0
    #     while sysactive:
    #         rdr.wait_for_tag()
    #         (error, data) = rdr.request()
    #         if not error:
    #             print("\nDetected: " + format(data, "02x"))
    #         (error, uid) = rdr.anticoll()
    #         if not error:
    #             cards.put(":".join([str(id) for id in uid]))
    #             #GPIO.output(11,True)
    #             time.sleep(.2)
    #             GPIO.output(11,False)
    #         time.sleep(.8)
    #start_thread(readpi)
    
    ## This supports your standard RC522 connected to the GPIO as per various online articles...
    #import RPi.GPIO as GPIO
    # from mfrc522 import SimpleMFRC522
    # def read13():
    #     reader = SimpleMFRC522()
    #     while sysactive:
    #         try:
    #             id, text = reader.read()
    #             cards.put(id)
    #         finally:
    #             GPIO.cleanup()
    # #start_thread(read13)

    ## This supports the SB Components RFID Hat
    # import serial  
    # def read125():
    #     def read_rfid():
    #         ser = serial.Serial ("/dev/ttyS0")                           
    #         ser.baudrate = 9600                                          
    #         data = ser.read(12)                                          
    #         ser.close ()                                                 
    #         data=data.decode("utf-8")
    #         return data                                                  
    #     while sysactive:
    #         id = read_rfid ()                                            
    #         cards.put(id)
    #start_thread(read125)

    pass
except: 
    pass
