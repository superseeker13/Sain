import time
import copy
import socket
import sys
import traceback

import color_hex
import remoteAPI

PreRead = 0
PostRead = 1
PreWrite = 2
PostWrite = 3
PreExecute = 4
PostExecute = 5

_Activate = 1
_Deactivate = 3
_Stop = 5
_Access = 9  
_Controllers = 11  
_Frame = 13  
_Scanline = 15  
_ScanlineCycle = 17  
_SpriteZero = 19
_Status = 21

_EVENT_TYPES = [ _Activate, _Deactivate, _Stop, _Access, _Controllers, 
    _Frame, _Scanline, _ScanlineCycle, _SpriteZero, _Status ]

_EVENT_REQUEST = 0xFF
_EVENT_RESPONSE = 0xFE
_HEARTBEAT = 0xFD
_READY = 0xFC
_RETRY_SECONDS = 1

_BLOCK_SIZE = 4096
_ARRAY_LENGTH = 1024

_host = None
_port = -1
_remoteAPI = None

def _isNotBlank(s):
  return s and s.strip()

def initRemoteAPI(host, port):
  global _host
  global _port
  _host = host
  _port = port
  
def getAPI():
  global _remoteAPI
  if _remoteAPI == None and _isNotBlank(_host):
    _remoteAPI = remoteAPI._RemoteAPI(_host, _port)
  return _remoteAPI

class _AccessPoint(object):

  def __init__(self, listener, accessPointType, minAddress, maxAddress = -1, 
      bank = -1):
    self.listener = listener;
    self.accessPointType = accessPointType;
    self.bank = bank;
    
    if maxAddress < 0:
      self.minAddress = self.maxAddress = minAddress
    elif minAddress <= maxAddress:
      self.minAddress = minAddress
      self.maxAddress = maxAddress
    else:
      self.minAddress = maxAddress
      self.maxAddress = minAddress
      
class _ScanlineCyclePoint(object):
  
  def __init__(self, listener, scanline, scanlineCycle):
    self.listener = listener
    self.scanline = scanline
    self.scanlineCycle = scanlineCycle
    
class _ScanlinePoint(object):

  def __init__(self, listener, scanline):
    self.listener = listener
    self.scanline = scanline

class _DataStream(object):
  
  def __init__(self, sock):
    self._readBuffer = bytearray()
    self._writeBuffer = bytearray()
    self._sock = sock
    
  def _close(self):
    self._sock.shutdown()
    self._sock.close()
    
  def _fillReadBuffer(self, count):
    while len(self._readBuffer) < count:
      block = self._sock.recv(_BLOCK_SIZE)
      if len(block) == 0:
        raise IOError("Disconnected.")
      self._readBuffer.extend(block)
      
  def _read(self):
    return self._readBuffer.pop(0)
      
  def writeByte(self, value):
    self._writeBuffer.append(value & 0xFF)
      
  def readByte(self) -> int:
    self._fillReadBuffer(1)
    return self._read()
  
  def writeInt(self, value):
    self.writeByte(value >> 24)
    self.writeByte(value >> 16)
    self.writeByte(value >> 8)
    self.writeByte(value)
  
  def readInt(self) -> int:
    self._fillReadBuffer(4)
    value = self._read() << 24
    value |= self._read() << 16
    value |= self._read() << 8
    value |= self._read()
    return value
  
  def writeIntArray(self, array):
    self.writeInt(len(array))
    for i in range(len(array)):
      self.writeInt(array[i])
      
  def readIntArray(self, array):
    length = self.readInt()
    if length < 0 or length > len(array):
      self._close()
      raise IOError("Invalid array length: %d" % length)
    for i in range(length):    
      array[i] = self.readInt()
    return length
  
  def writeBoolean(self, value):
    self.writeByte(1 if value else 0)
  
  def readBoolean(self):
    return self.readByte() != 0
  
  def writeChar(self, value):
    self.writeByte(ord(value[0]))
  
  def readChar(self) -> chr:
    return chr(self.readByte())
  
  def writeCharArray(self, array):
    self.writeString(array)
      
  def readCharArray(array):
    length = self.readInt()
    if length < 0 or length > len(array):
      self._close()
      raise IOError("Invalid array length: %d" % length)
    for i in range(length):    
      array[i] = self.readChar()
    return length 
  
  def writeString(self, value):
    self.writeInt(len(value))
    for i in range(len(value)):
      self.writeByte(ord(value[i]))
      
  def readString(self) -> str:
    length = self.readInt()
    if length < 0 or length > _ARRAY_LENGTH:
      self._close()
      raise IOError("Invalid array length: %d" % length)
    cs = bytearray()
    for i in range(length):
      cs.append(self.readByte())
    return str(cs)
  
  def writeStringArray(self, array):
    self.writeInt(len(array))
    for i in range(len(array)):
      self.writeString(array[i])
      
  def readStringArray(self, array) -> int:
    length = self.readInt()
    if length < 0 or length > len(array):
      self._close()
      raise IOError("Invalid array length: %d" % length)
    for i in range(length):
      array[i] = self.readString()
    return length
  
  def readDynamicStringArray(self):
    length = self.readInt()
    if length < 0 or length > _ARRAY_LENGTH:
      self._close()
      raise IOError("Invalid array length: %d" % length)
    array = []
    for i in range(length):
      array.append(self.readString())
    return array  
  
  def flush(self):
    self._sock.sendall(self._writeBuffer)
    del self._writeBuffer[:]    
    
class _RemoteBase(object):
      
  def __init__(self, host, port):
    self._host = host
    self._port = port
    self._stream = None
    self._nextID = 0
    self._listenerIDs = {}
    self._running = False
    
    # eventType -> listenerID -> listenerObject(listener)
    self._listenerObjects = { eventType : {} for eventType in _EVENT_TYPES }
    
  def run(self):
    if self._running:
      return
    else:
      self._running = True
    while True:
      self._fireStatusChanged("Connecting to %s:%d..." 
          % (self._host, self._port))
      sock = None
      try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._host, self._port))
        self._stream = _DataStream(sock)
      except:
        self._fireStatusChanged("Failed to establish connection.")
      if self._stream != None:
        try:
          self._fireStatusChanged("Connection established.")
          self._sendListeners()
          self._sendReady()
          while True:
            self._probeEvents()
        except IOError:
          self._fireDeactivated()
          self._fireStatusChanged("Disconnected.")
        except:
          ex_type, ex_value, ex_traceback = sys.exc_info()
          trace_back = traceback.extract_tb(ex_traceback)
          print("%s: %s" % (ex_type.__name__, ex_value))
          for trace in trace_back:
            print("  File \"%s\", line %d, in %s" 
                % (trace[0], trace[1], trace[2]))
            print("    %s" % trace[3])
          self._fireDeactivated()
          self._fireStatusChanged("Disconnected.")
        finally:
          self._stream = None
      time.sleep(_RETRY_SECONDS)   
      
  def _fireDeactivated(self):
    for listenerID, listener in copy.copy(self._listenerObjects[_Deactivate]
        .items()):
      listener()
  
  def _fireStatusChanged(self, message):
    for listenerID, listener in copy.copy(self._listenerObjects[_Status]
        .items()):
      listener(message)
      
  def _sendReady(self):
    if self._stream != None:
      try:
        self._stream.writeByte(_READY)
        self._stream.flush()
      except:
        pass   
      
  def _sendListeners(self):
    for eventType, listObjs in self._listenerObjects.items():
      for listenerID, listenerObject in listObjs.items():
        self._sendListener(listenerID, eventType, listenerObject)
        
  def _probeEvents(self):
    
    self._stream.writeByte(_EVENT_REQUEST)
    self._stream.flush()
    
    eventType = self._stream.readByte()
    
    if eventType == _HEARTBEAT:
      self._stream.writeByte(_EVENT_RESPONSE)
      self._stream.flush()
      return
    
    listenerID = self._stream.readInt()
    obj = self._listenerObjects[eventType].get(listenerID, None)
    
    if obj != None:
      if eventType == _Access:
        accessPointType = self._stream.readInt()
        address = self._stream.readInt()
        value = self._stream.readInt()
        result = obj.listener(accessPointType, address, value)
        self._stream.writeByte(_EVENT_RESPONSE)
        self._stream.writeInt(result)
      else:
        if (   eventType == _Activate 
            or eventType == _Deactivate 
            or eventType == _Stop
            or eventType == _Controllers
            or eventType == _Frame):
          obj()
        elif eventType == _Scanline:
          obj.listener(self._stream.readInt())
        elif eventType == _ScanlineCycle:
          obj.listener(self._stream.readInt(), self._stream.readInt(), 
              self._stream.readInt(), self._stream.readBoolean())
        elif eventType == _SpriteZero:
          obj.listener(self._stream.readInt(), self._stream.readInt())
        elif eventType == _Status:
          obj.listener(self._stream.readString())
        else:
          raise IOError("Unknown listener type: %d" % eventType)

        self._stream.writeByte(_EVENT_RESPONSE)
    
    self._stream.flush()        
        
  def _sendListener(self, listenerID, eventType, listenerObject):
    if self._stream != None:
      try:
        self._stream.writeByte(eventType)
        self._stream.writeInt(listenerID)
        if eventType == _Access:
          self._stream.writeInt(listenerObject.accessPointType)
          self._stream.writeInt(listenerObject.minAddress)
          self._stream.writeInt(listenerObject.maxAddress)
          self._stream.writeInt(listenerObject.bank)
        elif eventType == _Scanline:
          self._stream.writeInt(listenerObject.scanline)
        elif eventType == _ScanlineCycle:
          self._stream.writeInt(listenerObject.scanline)
          self._stream.writeInt(listenerObject.scanlineCycle)
        self._stream.flush()
      except:
        pass
      
  def _addListener(self, listener, eventType):
    if listener != None:
      self._sendListener(self._addListenerObject(listener, eventType), 
          eventType, listener)

  def _removeListener(self, listener, eventType, methodValue):
    if listener != None:
      listenerID = self._removeListenerObject(listener, eventType)
      if listenerID >= 0 and self._stream != None:
        try:
          self._stream.writeByte(methodValue)
          self._stream.writeInt(listenerID)
          self._stream.flush()
        except:
          pass
  
  def _addListenerObject(self, listener, eventType, listenerObject = None):
    if listenerObject == None:
      listenerObject = listener
    listenerID = self._nextID
    self._nextID += 1
    self._listenerIDs[listener] = listenerID
    self._listenerObjects[eventType][listenerID] = listenerObject
    return listenerID
  
  def _removeListenerObject(self, listener, eventType) -> int:
    listenerID = self._listenerIDs.pop(listener, None)
    if listenerID != None:
      self._listenerObjects[eventType].pop(listenerID)
      return listenerID
    else:
      return -1
      
  def addActivateListener(self, listener):
    self._addListener(listener, _Activate)

  def removeActivateListener(self, listener):
    self._removeListener(listener, _Activate, 2)

  def addDeactivateListener(self, listener):
    self._addListener(listener, _Deactivate)

  def removeDeactivateListener(self, listener):
    self._removeListener(listener, _Deactivate, 4)

  def addStopListener(self, listener):
    self._addListener(listener, _Stop)

  def removeStopListener(self, listener):
    self._removeListener(listener, _Stop, 6)
  
  def addAccessPointListener(self, listener, accessPointType, minAddress, 
      maxAddress = -1, bank = -1):    
    if listener != None:
      point = _AccessPoint(listener, accessPointType, minAddress, maxAddress, 
          bank)
      self._sendListener(self._addListenerObject(listener, _Access, point), 
          _Access, point)

  def removeAccessPointListener(self, listener):
    self._removeListener(listener, _Access, 10)

  def addControllersListener(self, listener):
    self._addListener(listener, _Controllers)

  def removeControllersListener(self, listener):
    self._removeListener(listener, _Controllers, 12)

  def addFrameListener(self, listener):
    self._addListener(listener, _Frame)

  def removeFrameListener(self, listener):
    self._removeListener(listener, _Frame, 14)
  
  def addScanlineListener(self, listener, scanline):
    if listener != None:
      point = _ScanlinePoint(listener, scanline)
      self._sendListener(self._addListenerObject(listener, _Scanline, point), 
          _Scanline, point)

  def removeScanlineListener(self, listener):
    self._removeListener(listener, _Scanline, 16)
  
  def addScanlineCycleListener(self, listener, scanline, scanlineCycle):    
    if listener != None:
      point = _ScanlineCyclePoint(listener, scanline, scanlineCycle)
      self._sendListener(self._addListenerObject(listener, _ScanlineCycle, 
          point), _ScanlineCycle, point)
  
  def removeScanlineCycleListener(self, listener):
    self._removeListener(listener, _ScanlineCycle, 18)
  
  def addSpriteZeroListener(self, listener):
    self._addListener(listener, _SpriteZero)

  def removeSpriteZeroListener(self, listener):
    self._removeListener(listener, _SpriteZero, 20)

  def addStatusListener(self, listener):
    self._addListener(listener, _Status)

  def removeStatusListener(self, listener):
    self._removeListener(listener, _Status, 22)

  def getPixels(self, pixels):
    try:
      self._stream.writeByte(119)
      self._stream.flush()
      self._stream.readIntArray(pixels)
    except:
      pass
