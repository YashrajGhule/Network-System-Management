import colorama

class Logger:
    def logInfo(self,msg):
        print(colorama.Fore.BLUE + "[INFO] " + colorama.Fore.WHITE + msg)
    
    def logError(self,msg):
        print(colorama.Fore.RED + "[ERROR] " + colorama.Fore.WHITE + msg)
        
    def logWarning(self,msg):
        print(colorama.Fore.YELLOW + "[WARNING] " + colorama.Fore.WHITE + msg)
    
    def logSuccess(self,msg):
        print(colorama.Fore.GREEN + "[SUCCESS] " + colorama.Fore.WHITE + msg)
        
if __name__ == "__main__":
    logger = Logger()
    logger.logInfo("This is an info message")
    logger.logError("This is an error message")
    logger.logWarning("This is a warning message")
    logger.logSuccess("This is a success message")