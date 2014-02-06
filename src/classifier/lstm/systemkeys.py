import uinput
import time
import properties.config as c

'''
Class to provide an interface to simulate a keyboard stroke to the system. 
Uses uinput library
'''
class SystemKeys():

    def __init__(self):
        self.keys = self.createKeyBindings()
        usedKeys = []
        for val in self.keys.values():
            if val != None:
                usedKeys.append(val)
        self.device = uinput.Device(usedKeys)
        time.sleep(1)
        # End counter is to terminate system key activation after 10 times --> for testing
        self.endCounter = 0
        self.enableEndCounter = False

    '''
    outputs the key for specific class. 
    If counter is enabled this will work only 10 times (counter is necesary for some testing purposes)
    '''
    def outForClass(self, clazz):
        if(self.enableEndCounter):
            if(self.endCounter <= 10):
                self.endCounter += 1
                if(self.keys[clazz] != None):
                    self.device.emit_click(self.keys[clazz])
        else:
            if(self.keys[clazz] != None):
                self.device.emit_click(self.keys[clazz])

    '''
    Bind keys to classes. 
    '''
    def createKeyBindings(self):
        keys = {}
        config = c.getInstance().getConfig("keys")
        keys[0] = eval(config.get("key_0"))
        keys[1] = eval(config.get("key_1"))
        keys[2] = eval(config.get("key_2"))
        keys[3] = eval(config.get("key_3"))
        keys[4] = eval(config.get("key_4"))
        keys[5] = eval(config.get("key_5"))
        keys[6] = eval(config.get("key_6"))
        keys[7] = eval(config.get("key_7"))
        return keys
