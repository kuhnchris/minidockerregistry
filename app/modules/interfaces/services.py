class CommonServiceInterface():
    def __init__(self) -> None:
        self.threadObject = None
        
    def getService(self):
        return

    def threadFunction(self):
        raise NotImplementedError
    
    def stopThread(self):
        raise NotImplementedError
    
    def startThread(self):
        raise NotImplementedError
    
    def startService(self):
        raise NotImplementedError
