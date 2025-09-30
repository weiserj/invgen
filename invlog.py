
import logging
import logging.handlers
import sys 

def loggerTest():
    ### Test deslogging Paketes
    # Erzeugen des Loggers und der beiden Hadler (stream und File)
    logger = logging.getLogger("blabla")
    sh = logging.StreamHandler(stream=sys.stdout)    
    fh = logging.FileHandler("test.log", mode="w", encoding="utf-8" )
    # Formatter Klasse definieren
    fmt = '{name} {funcName} {levelname} {message} {lineno}'
    pformat = logging.Formatter(fmt, style='{')    
    # Formatter - Klasse zu beiden Message-Handler dazufügen
    sh.setFormatter(pformat)
    fh.setFormatter(pformat)
    # FileHandler zu Logger hinzufügen
    logger.addHandler(sh)
    logger.addHandler(fh)
    # Logging-Level festsetzen
    logger.setLevel(logging.INFO)
    # 2 Messgaes absetzen,wird nicht gemacht,
    # do_any(logger)
    return logger

def do_any(l):
    l.info("Hello World-Info!")
    l.warning("Hello World - Warning!!!!!?")

if __name__ == '__main__':
    loggerTest()
