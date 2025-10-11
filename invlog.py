
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
    fmt = '{name} {funcName} {levelname} {asctime} {message} {lineno}'
    pformat = logging.Formatter(fmt, style='{')    
    # Formatter - Klasse zu beiden Message-Handler dazufügen
    sh.setFormatter(pformat)
    fh.setFormatter(pformat)
    # FileHandler zu Logger hinzufügen
    logger.addHandler(sh)
    logger.addHandler(fh)
    # Logging-Level festsetzen
    # loggging Levels: DEBUG, INFO WARNING, ERROR, CRITTICAL
    logger.setLevel(logging.INFO)
    # 2 Messgaes absetzen,wird nicht gemacht,
    # do_any(logger)

    logger2 = logging.getLogger("Test2") 
    sh2 = logging.StreamHandler(stream=sys.stdout)    
    fh2 = logging.FileHandler("test2.log", mode="w", encoding="utf-8" )
    # pformat2 = logging.Formatter(fmt, style='{')
    sh2.setFormatter(pformat)
    fh2.setFormatter(pformat)
    logger2.addHandler(sh2)
    logger2.addHandler(fh2)

    return {'logger': logger, 'logger2': logger2}

def do_any(l):
    l.info("Hello World-Info!")
    l.warning("Hello World - Warning!!!!!?")

if __name__ == '__main__':
    d = loggerTest()
    logger =  d["logger"]
    logger2 =d['logger2']
    do_any(logger2)
    print(logger2.getEffectiveLevel())
    logger.setLevel(logging.INFO)
