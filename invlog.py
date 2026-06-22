
import logging
import logging.handlers
import sys 

def loggerTest():
    # Bedeutung im Detail nicht ganz klar! Kann man vermutlich wieder qeglasse!
    global logger
    global logger2

    ### Test des logging Paketes
    # Erzeugen des Loggers und der beiden Hadler (stream und File)
    logger = logging.getLogger("blabla")
    sh = logging.StreamHandler(stream=sys.stdout)    
    fh = logging.FileHandler("test.log", mode="w", encoding="utf-8" )
    # Formatter Klasse definieren, d.h. wie die Ausgabe formatiert wird.
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
    do_any(logger)

    
    
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
    do_any(logger)

# just a testline to check if file visible for staging/commiting in git/github

def debugEdaListe(header, privateList):
    logger2.info(f"***   {header}   ***")
    for privateElem in privateList:
        logger2.info(f"NEW Name:{privateElem['Name']}   Vorname:{privateElem['Vorname']}")
        for edaElem in privateElem['edaListeNehmer']:
            logger2.info(f"NEW Zählpunkt:{edaElem['Zählpunkt']}   Energierichtung:{edaElem['Energierichtung']}")
            logger2.info(f"Verbrauch:{edaElem['Verbrauch']}") if 'Verbrauch' in edaElem else "Verbrauch in edaElem missing"
            logger2.info(f"Lieferung:{edaElem['Lieferung']}") if 'Lieferung' in edaElem else "Lieferung in edaElem missing"
            logger2.info(f"preisBrutto:{edaElem['preisBrutto']}") if 'preisBrutto' in edaElem else "preisBrutto in edaElem missing"
        for edaElem in privateElem['edaListeGeber']:
            logger2.info(f"NEW Zählpunkt:{edaElem['Zählpunkt']}   Energierichtung:{edaElem['Energierichtung']}")
            logger2.info(f"Verbrauch:{edaElem['Verbrauch']}") if 'Verbrauch' in edaElem else "Verbrauch in edaElem missing"
            logger2.info(f"Lieferung:{edaElem['Lieferung']}") if 'Lieferung' in edaElem else "Lieferung in edaElem missing"
            logger2.info(f"preisBrutto:{edaElem['preisBrutto']}") if 'preisBrutto' in edaElem else "preisBrutto in edaElem missing"
    pass
    
    #debugging the privateList tabel!!
def debugPrivateList(header, privateList):
    global logger
    global logger2
    logger2.info(f"***   {header}   ***")
    # logger2.setLevel(logging.INFO)
    for privateElem in privateList:
        logger2.info(f"Name:{privateElem['Name']}   Vorname:{privateElem['Vorname']}")

        logger2.info(f"summePreisBruttoExists:{privateElem['summePreisBruttoExists']}") \
            if 'summePreisBruttoExists' in privateElem else logger2.info('summePreisBruttoExists does not exist')
        logger2.info(f"summePreisBrutto:{privateElem['summePreisBrutto']}") \
            if 'summePreisBrutto' in privateElem else logger2.info('summePreisBrutto does not exist')
        logger2.info(f"summePreisBruttoText:{privateElem['summePreisBruttoText']}") \
            if 'summePreisBruttoText' in privateElem else logger2.info('summePreisBruttoText does not exist')


        """ if 'summePreisBruttoExists' in privateElem:
            logger2.info(f"summePreisBruttoExists:{privateElem['summePreisBruttoExists']}   summePreisBrutto:{privateElem['summePreisBrutto']}")
            logger2.info(f"summePreisBruttoText:{privateElem['summePreisBruttoText']}")
        else:
            logger2.info('summePreisBruttoExists is missing') """
        
        logger2.info(f"summeVerbrauchExists:{privateElem['summeVerbrauchExists']}") \
            if 'summeVerbrauchExists' in privateElem else logger2.info('summeVerbrauchExists does not exist')
        logger2.info(f"summeVerbrauch:{privateElem['summeVerbrauch']}") \
            if 'summeVerbrauch' in privateElem else logger2.info('summeVerbrauch does not exist')
        logger2.info(f"summeVerbrauchText:{privateElem['summeVerbrauchText']}") \
            if 'summeVerbrauchText' in privateElem else logger2.info('summeVerbrauchText does not exist')

        logger2.info(f"summeLieferungExists:{privateElem['summeLieferungExists']}") \
            if 'summeLieferungExists' in privateElem else logger2.info('summeLieferungExists does not exist')
        logger2.info(f"summeLieferung:{privateElem['summeLieferung']}") \
            if 'summeLieferung' in privateElem else logger2.info('summeLieferung does not exist')
        logger2.info(f"summeLieferungText:{privateElem['summeLieferungText']}") \
            if 'summeLieferungText' in privateElem else logger2.info('summeLieferungText does not exist')

        """ if 'summeVerbrauchExists' in privateElem:   
            logger2.info(f"summeVerbrauchExists:{privateElem['summeVerbrauchExists']}")
            logger2.info(f"summeVerbrauch:{str(privateElem['summeVerbrauch'])}   summeVerbrauchText:{privateElem['summeVerbrauchText']}")
        else:
            logger2.info('summeVerbrauchExists is missing')

        if 'summeLieferungExists' in privateElem: 
            logger2.info(f"summeLieferungExists:{privateElem['summeLieferungExists']}   summeLieferung:{privateElem['summeLieferung']}")
            logger2.info(f"summeLieferungText:{privateElem['summeLieferungText']}")
        else:
            logger2.info('summeLieferungExists is missing') """
    pass