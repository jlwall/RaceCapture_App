import serial
from threading import Thread, RLock
from serial.tools import list_ports
from rcpconfig import VersionConfig

DEFAULT_READ_RETRIES = 2
DEFAULT_SERIAL_WRITE_TIMEOUT = 0
DEFAULT_SERIAL_READ_TIMEOUT = None

class serial_comms():
    port = None
    ser = None
    timeout = DEFAULT_SERIAL_READ_TIMEOUT
    writeTimeout = DEFAULT_SERIAL_WRITE_TIMEOUT
 

    def __init__(self, **kwargs):
        self.port = kwargs.get('port', self.port)
    
    def setPort(self, port):
        self.port = port
    
    def getPort(self):
        return self.port
    
    def isOpen(self):
        return not self.ser == None
    
    def open(self):
        print('Opening serial')
        if self.port == None:
            self.autoDetectWorker()
            if self.port == None:
                self.ser = None
                raise Exception('Could not open port: Device not detected')
        else:
            ser = serial.Serial(self.port, timeout=self.timeout, writeTimeout = self.writeTimeout) 
            ser.flushInput()
            ser.flushOutput()
            self.ser = ser
    
    def close(self):
        if self.ser != None:
            self.ser.close()
        self.ser = None
    
    def readLine(self):
        ser = self.ser
        eol2 = b'\r'
        retryCount = 0
        line = bytearray()

        while True:
            c = ser.read(1)
            if  c == eol2:
                break
            elif c == '':
                if retryCount >= self.retryCount:
                    self.close()
                    raise Exception('Could not read line')
                retryCount +=1
                print('Timeout - retry: ' + str(retryCount))
                print("POKE")
                ser.write(' ')
            else:
                line += c
                
        line = bytes(line).strip()
        line = line.replace('\r', '')
        line = line.replace('\n', '')
        return line
    
    def write(self, data):
        return self.ser.write(data)
    
    def flushInput(self):
        self.ser.flushInput()
    
    def flushOutput(self):
        self.ser.flushOutput()
    
    def autoDetect(self, getVersion, winCallback, failCallback):
        t = Thread(target=self.autoDetectWorker, args=(getVersion, winCallback, failCallback))
        t.daemon = True
        t.start()        
        
    def autoDetectWorker(self, getVersion, winCallback = None, failCallback = None):
        if self.port:
            ports = [self.port]
        else:
            ports = [x[0] for x in list_ports.comports()]

        self.retryCount = 0
        self.timeout = 0.5
        self.writeTimeout = 0
        print "Searching for device on all serial ports"
        testVer = VersionConfig()
        verJson = None
        for p in ports:
            try:
                print "Trying", p
                self.port = p
                self.open()
                verJson = getVersion(True)
                testVer.fromJson(verJson.get('ver', None))
                if testVer.major > 0 or testVer.minor > 0 or testVer.bugfix > 0:
                    break
                
            except Exception as detail:
                print('Not found on ' + str(p) + " " + str(detail))
                try:
                    self.close()
                    self.port = None
                finally:
                    pass

        self.retryCount = DEFAULT_READ_RETRIES
        self.timeout = DEFAULT_SERIAL_READ_TIMEOUT
        self.writeTimeout = DEFAULT_SERIAL_WRITE_TIMEOUT
        if not verJson == None:
            print "Found device version " + testVer.toString() + " on port:", self.port
            self.close()
            if winCallback: winCallback(testVer)
        else:
            self.port = None
            if failCallback: failCallback()
        