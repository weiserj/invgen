import pandas as pd
from spire.xls import *
from spire.xls.common import *
from jinja2 import Environment, FileSystemLoader
import csv
import html
import weasyprint
import pathlib
import datetime
import time
import invlog

class Configuration:
    # Liste der Spaltenüberschriften,
    # Bezeichnung besser edaNames
    rowstr = ['Zählpunkt', 'Energierichtung',  # 0,1
              'Restüberschuss bei EG und je ZP [KWH]',  # 2
              'Eigendeckung gemeinschaftliche Erzeugung [KWH]',  # 3
              'Gesamte gemeinschaftliche Erzeugung [KWH]'  # 4
              ]

    def __init__(self):
        self.homeDir = '/home/johann/invgen'
        # homeDir2 ist kein git-Directory (wie homeDir)
        self.homeDir2 = '/home/johann/nogit'
        # Input für invgen!! 
        self.dataDir = self.homeDir + '/data'
        self.mitgliederXlsx = self.dataDir + '/Mitgliederliste-Reidlinger.xlsx'
        # alle im Lauf der Generierung erzeugten Daten sind nun im nogit-Teil!!
        self.interm = self.homeDir2 + '/intermediate'
        self.mitgliederCsv = self.interm + '/Mitgliederliste-Reidlinger.csv'
        self.templateDir = self.homeDir + '/templates/'
        self.resultDir = self.homeDir2 + '/results'
        self.edaDataDir = self.dataDir + '/Reidlinger/neuesFormat'
        #nun kommt die Liste der eda-Daten-Files
        # ein solches File pro Monat!
        self.inventYear = 2025
        self.inventMonthFirst = 1
        self.inventMonthLast = 1
        # RC_Nummer ='RC103316' # für Wilhelmsdorf-Weiser
        # RC_Nummer ='RC103317' # für Poysdorf-Weiser
        self.RC_Nummer ='RC100122' # für Reidlinger
        
        # AT00200000000RC100122000000000037_20240601_20240630_202407111405.xlsx'
        # self.edaFileFull = self.dataDir + '/' + self.edaFile
        self.edaUebersicht = self.interm + '/edaUebersicht.csv'
        self.edaPart1 = self.interm + '/edaPart1.csv'
        self.edaPart2 = self.interm + '/edaPart2.csv'
        
    def createBasicDirectories(self):
        # erzeugt alle Ausgabedrectories soferne sie nicht existieren
        #im Moment nur der Anfang
        p = pathlib.Path(self.interm)
        if not p.exists():
           p.mkdir(parents=True)
        p = pathlib.Path(self.resultDir)
        if not p.exists():
           p.mkdir(parents=True)
        pass

    def printAll(self):
        print()
        print("General Configuration: class Configuration:")
        print("homeDir = ", self.homeDir)
        print("dataDir = ", self.dataDir)
        print("mitgliederXlsx = ", self.mitgliederXlsx)
        print("mitgliederCsv =", self.mitgliederCsv)
        print("intermediateDir = ", self.interm)
        print("templateDir = ", self.templateDir)
        print("resultDir = ", self.resultDir)
        print("edaDataDir = ", self.edaDataDir)
        print("inventYear = ", self.inventYear)
        print("inventMonthFirst = ",self.inventMonthFirst)
        print("inventMonthLast = ",self.inventMonthLast)
        print()

class GenerationData:
    def __init__(self):
        # edaList ist die Liste der EDA-Einträge, einen pro Zählpunkt
        # edaDict ist das Dictionary, mit dem man über den Zählpunkt zugreifen kann
        # privateList ist die Liste der Mitglieder: Grundsätzlich gibt es pro Zeile (ohne
        # Folgezeilenkennzeichnung eine Eintrag
        # privateDict ist weider das Dictionary mit dem direkten Zugriff über den Zählpunkt
        # Wenn jemand mehrere Zählpunkte
        #print("class GenerationData: ")
        self.edaList = []
        self.edaDict = {}
        self.privateList = []
        self.privateDict = {}
        # die Liste der Dateien(jede für 1 Monat)
        self.edaFileList = []
        self.edaFilesOkay = True

    def structTime_TO_dateTime(self, st):
        return datetime.datetime(st.tm_year, st.tm_mon, st.tm_mday, st.tm_hour, st.tm_min, st.tm_sec)

    def addEdaElem(self, elem):
        # Es wird ein eda-Element hinzugefügt
        # Es wird sichergestellt dass es dafür zumindest einen dummy-Zählpunkt gibt
        self.edaList.append(elem)
        if type(elem) == dict:
            elem.update({'index': len(self.edaList)})
            logger.info(f"{elem}")
            if 'Zählpunkt' not in elem:
                elem.update({'Zählpunkt': 'AAA000'})
        self.edaDict.update({elem['Zählpunkt']:elem})
        # Testausgabe
        logger.info(f"edaZählpunkt:, {elem['Zählpunkt']}")

    def addPrivateElem(self, elem):
        '''
        :param elem:
        :return:
        Änderungen:
        - statt edaListe gibt es edaListeGeber und edaListeNehmer
        - es gibt 2 boolesche Falgs edaListeGeberFlag und edaListeNehmerFlag: sie dienen zurSteuerung in test2.html
        '''
        self.privateList.append(elem)
        if type(elem) == dict:
            elem.update({'index': len(self.privateList)})
            print(elem)
            if 'Zählpunkt' not in elem:
                elem.update({'Zählpunkt': 'AAA000'})
        self.privateDict.update({elem['Zählpunkt']:elem})


        zaehlpunkt = elem['Zählpunkt']
        edaElem = self.edaDict[zaehlpunkt]
        # ListE der Zählpunkte  bis jetzt nur einen
        #edaListe = [edaElem]
        #elem.update({'edaData': edaListe})
        # Korrektur
        elem['edaListeNehmerFlag'] = False
        elem['edaListeGeberFlag'] = False
        elem['edaListeNehmer'] =[]
        elem['edaListeGeber'] = []
        zaehlpunkt = elem['Zählpunkt']
        edaElem = self.edaDict[zaehlpunkt]
        if edaElem[Configuration.rowstr[1]] == 'CONSUMPTION':
            elem['edaListeNehmerFlag'] = True
            elem['edaListeNehmer'].append(edaElem)
        else:
            elem['edaListeGeberFlag'] = True
            elem['edaListeGeber'].append(edaElem)

        #diese Listen als Komponente edaData eintragen
        #
        # elem ist das privateElem - nichts zu tun
        # elem  #die Komponente
        # den Zählpunkterhalten wir mit der Komponente Zählpunkt:
        # zählpunkt = elem['Zählpunkt']
        # mit dem Zählpunkt können wir auf die edaList zugreifen
        # edaElem = edaDict['AT002...Zählpunkt']

        # elem.update(elem['Zählpunkt']:self.edaDict['Zählpunkt'])
        #elem.update("edaData":[self.edaDict['Zählpunkt']])

    def addZaehlpunkt(self, zpMain, zp2):
        '''
        :param zpMain:
        :param zp2:
        :return:
        '''
        # ein Zählpunkt wirdzu einem Mitglied (privateElem ) hinzugefügt
        privateElem = self.privateDict[zpMain]
        #edaList = privateElem['edaData']
        edaElem = self.edaDict[zp2]
        if edaElem[Configuration.rowstr[1]] == 'CONSUMPTION':
            privateElem['edaListeNehmerFlag'] = True
            privateElem['edaListeNehmer'].append(edaElem)
        else:
            elem['edaListeGeberFlag'] = True
            elem['edaListeGeber'].append(edaElem)
        #edaList = privateElem['edaData']
        #edaList.append(edaElem)

    def addRabatt2(self, rabattNehmerZp, rabattGeberZp):
        self.rl = RabattLink()
        self.rl.updateGeberZp(rabattGeberZp)
        self.rl.updateNehmerZp(nehmerZp)
        self.rl.updateEdaTransfer(edaData, row)

    def addRabatt(self, row):
        # das ist die neuere Version, die Werte sind in row gespeichert
        edaElem = self.edaDict[row['Rabatt-Zaehlernummer']]
        privateElemGeber = self.privateDict[row['mainZp']]
        privateElemNehmer = self.privateDict[row['Rabatt-Zaehlernummer']]
        if 'rabattGeber' not in privateElemNehmer:
            privateElemNehmer['rabattGeber'] = []
        #privateElemNehmer['rabattGeber'].append(edaElem)
        privateElemNehmer['rabattGeber'].append(row)
        row['edaElem'] = edaElem
        #if 'rabattGeber' not in privateElemNehmer:
        #    privateElemNehmer['rabattGeber'] = []
        ## privateElemNehmer['rabattGeber'].append(edaElem)
        #privateElemNehmer['rabattGeber'].append(row)
        if 'rabattNehmer' not in privateElemGeber:
            privateElemGeber['rabattNehmer'] = []
        privateElemGeber['rabattNehmer'].append(row)

        pass

    def addRabatt1(self, rabattNehmerZp, rabattGeberZp, row):
        # das Original
        # rabetNehmerZp: der Zählpunkt, für welchen die Zahlungen reduziert werden
        # rabattGeberZp: der Zählpunkt, welcher den Rabatt zahlt
        # Das edaElem, welches bei der Komponente rabattGeber und rabattnehmer
        # hinzugefügt wird
        # edaElem:Zahlungen, welche vom rabatGeber zum Rabatneher verschoben werden
        # Zusatz:
        #   - rabattGeberZp wir dauch als mainZp bezeichnet
        #   - rabattNehmerZp wird auch als rabattZp bezeichnet

        edaElem = self.edaDict[rabattNehmerZp]
        edaElem['rabattZeile'] = row   # dasist neu auch der Parameter row
        # die beiden Kunden, welche von den Zahlungsänderungen betroffen sind
        privateElemGeber = self.privateDict[rabattGeberZp]
        privateElemNehmer = self.privateDict[rabattNehmerZp]
        # Bei beiden Zählpunkten wir eine Liste von edaElems eingerichtet
        if 'rabattGeber' not in privateElemNehmer:
            privateElemNehmer['rabattGeber'] = []
        privateElemNehmer['rabattGeber'].append(edaElem)
        # das hier ist ausführlicher
        #listeElemNehmer = privateElemNehmer['rabattGeber']
        #listeElemNehmer.append(edaElem)
        if 'rabattNehmer' not in privateElemGeber:
            privateElemGeber['rabattNehmer'] = []
        privateElemGeber['rabattNehmer'].append(edaElem)
        print("*** edaElem: ", edaElem)
        print("*** edaElem-rabattZeile: ", edaElem['rabattZeile'])
        print("*** edaElem: ", privateElemGeber['rabattNehmer'])

    def addRabatt3(self, rabattNehmerZp, rabattGeberZp, row):
        # die neueste Version von addRabatt
        # es wird eine rabattStruct aus vier Komponenten erstellt:
        #rabattNehmer, rabattGeber, einzugehöriges edaElem für den rabattNehmer,
        # vielleicht auch für den rabattGeber und schließlich die aktuelle rabattZeile
        # es werden nicht die Zeiger auf die dictionaries gespeichert sondern
        # vermutlich die Pointer auf die Strukturen, so genau ist das in Python niccht
        # beschrieben
        rabattElem = {'rabattNehmer': self.privateDict[rabattNehmerZp],
                      'rabattGeber': self.privateDict[rabattGeberZp],
                      'edaData': self.edaDict[rabattNehmerZp],
                      'rabattZeile': row}
        # die beiden Kunden, welche von den Zahlungsänderungen betroffen sind
        privateElemGeber = self.privateDict[rabattGeberZp]
        privateElemNehmer = self.privateDict[rabattNehmerZp]
        # Bei beiden Zählpunkten wir eine Liste von edaElems eingerichtet
        if 'rabattGeber' not in privateElemNehmer:
            privateElemNehmer['rabattGeber'] = []
        privateElemNehmer['rabattGeber'].append(rabattElem)
        if 'rabattNehmer' not in privateElemGeber:
            privateElemGeber['rabattNehmer'] = []
        privateElemGeber['rabattNehmer'].append(rabattElem)

        value1 = -rabattElem['edaData']['Verbrauch']
        rabattElem['Verbrauch'] = value1
        rabattElem['VerbrauchText'] = "{value: >8.2f}".format(value=value1)
        value2 = -rabattElem['edaData']['preisBrutto']
        rabattElem['preisBrutto'] = value2
        rabattElem['preisBruttoText'] = "{value: >8.2f}".format(value=value2)

        #korektur des Prozentwertes auf ganze Zahlen
        #value = rabattElem['rabattZeile']['Rabatt']
        #print('value:', rabattElem['rabattZeile']['Rabatt'])
        #value1 = int(float(value))
        #print('value1', value1)
        rabattElem['rabattZeile']['Rabatt'] = int(float(rabattElem['rabattZeile']['Rabatt']))

        print("*** rabat-eda: ", rabattElem['edaData'])
        print("*** rabatt-Zeile: ", rabattElem['rabattZeile'])
        print("*** rabatt-Nehmer: ", rabattElem['rabattNehmer'])
        print("*** rabatt-Geber: ", rabattElem['rabattGeber'])
        pass


    def printAll(self):
        print("\nclass GenerationData:")

        # print(self.edaFileList)
        print();
        print(f"edaList: Länge = {len(self.edaList)}")
        for x in self.edaList:
            print(x['Zählpunkt'])
        print(f"edaDict: Länge = {len(self.edaDict)}")
        for x in self.edaDict:
            print(f"{{ Key:{x}: Value:{self.edaDict[x]} }}")
        print(f"privateList: Länge = {len(self.privateList)}")
        for x in self.privateList:
            print(x)
            for y in x['edaData']:
                print('!!!y ', y)
            if 'rabattGeber' in x:
                for y in x['rabattGeber']:
                    print('rabatGeber!!! ', y)
            if 'rabattNehmer' in x:
                for y in x['rabattNehmer']:
                    print('rabatNehmer!!! ', y)

        print(f"privateDict: Länge = {len(self.privateDict)}")
        for x in self.privateDict:
            print(f"{{ Key:{x}: Value:{self.privateDict[x]} }}")

        print('\nRabatt-Geber:')
        for x in self.privateList:
            if 'rabattGeber' in x:
                for y in x['rabattGeber']:
                    print('rabatGeber!!! ', y)
                    for z in y['edaElem']:
                        print('edaElem',z)

        print('\nRabatt-Nehmer:')
        for x in self.privateList:
            if 'rabattNehmer' in x:
                for y in x['rabattNehmer']:
                    print('rabattNehmer!!! ', y)
                    for z in y['edaElem']:
                        print('edaElem-Nehmer',z)

class RabattLink:
    def __init__(self):
        self.rabattNehmerZp = None
        self.rabattGeberZp = None
        self.nameGeber = None
        self.vornameGeber = None
        self.nameNehmer = None
        self.vornameNehmer = None
        self.preisNetto = None

    def updateNehmerZp (self, nehmerZp):
        privateElemNehmer  = self.privateDict[nehmerZp]
        print(privateElemNehmer)
        pass

    def updateGeberZp(self, geberZp):
        privateElemGeber = self.privateDict[geberZp]
        print(privateElemGeber)
        pass

    def updateEdaTransfer(self, edaData, row):
        print(edaData)
        print(row)
        pass

class InvoiceGeneration:

    def __init__(self):
        # class Configuration und class GenerationData erstellen
        # Rest derzeit in Kommentar, kommt später
        self.config = Configuration()
        # self.config.printAll()
        # print('Hello world!!')
        #! self.environment = Environment(loader=FileSystemLoader(self.config.templateDir))
        # das template kann auch erst später dazukommen
        #! self.template = self.environment.get_template("test2.html")
        self.gd = GenerationData()

    def checkEdaFiles(self):
        def daysOfMonth(self, year, month):
            if (month==1 or month== 3 or month==5 or month== 7 or month==8
                or month==10 or month==12):
                return 31
            if (month==4 or month== 6 or month==9 or month==11):
                return 30
            if (year%4==0):
                return 29
            else:
                return 28
            
        # begin of checkEdaFiles!!
        # Daten sind in GenerationData (Variable self.gd gespeichert)
        self.gd.edaFilesOkay = True           
        for actMonth in range(self.config.inventMonthFirst, self.config.inventMonthLast + 1):
            # print(actMonth)
            fileName =  \
                self.config.RC_Nummer + '_' + str(self.config.inventYear) + '-'+ f'{actMonth:02}' + '-1T00_00-'  \
                + str(self.config.inventYear) + '-'+ f'{actMonth:02}' + '-' + \
                f'{daysOfMonth(self, self.config.inventYear, actMonth)}T23_45.xlsx'
            # print(fileName)
            fileName = self.config.edaDataDir +"/" +fileName
            fileName2 = f'{self.config.RC_Nummer}_{actMonth:02}_Uebersicht.csv'
            fileName2 = f'{self.config.interm}/{fileName2}'
            fileName3 = f'{self.config.RC_Nummer}_{actMonth:02}_edaPart1.csv'
            fileName3 = f'{self.config.interm}/{fileName3}'
            fileName4 = f'{self.config.RC_Nummer}_{actMonth:02}_edaPart2.csv'
            fileName4 = f'{self.config.interm}/{fileName4}'
            d = {'fileName': fileName, 'month': actMonth, 'exists': True,
                 'ueberSicht':fileName2, 'edaPart1':fileName3, 'edaPart2':fileName4, 
                 'timeBeginExpected': datetime.datetime(self.config.inventYear,actMonth, 1, 0, 0),
                 'timeEndExpected': datetime.datetime(self.config.inventYear, actMonth,
                    daysOfMonth(self, self.config.inventYear, actMonth), 23, 45),
                 'timeBegin': None, 'timeEnd': None}
                
            p = pathlib.Path(fileName)
            if not p.exists():
                d['exists'] = False
                self.gd.edaFilesOkay = False
            self.gd.edaFileList.append(d)

        # Ausgabe der edaFiles!!
        print('edaFileList:')
        for edf in self.gd.edaFileList:
            print(edf)
        if self.gd.edaFilesOkay==False:
            print(f"****  edaFilesOkay={self.gd.edaFilesOkay}  ****")
            print("****   Some Files do not exist!!!!  ****")

        if self.gd.edaFilesOkay == False:
            raise Exception("Missing eda-File")
    
    def checkPeriods(self, fileList):
        # prüft, ob die Perioden genau einMonat sind bzw.  so wie im Namenenthalten!
        logger.info("Monatszeiten der EDA-Dateien prüfen")
        errorInChekPeriods = False
        for fileDesc in fileList:
            if fileDesc['timeBeginExpected'] != fileDesc['timeBegin']:
               logger.error(f"*** error with begin time, month {fileDesc['month']}")
               errorInChekPeriods = TextDirectionrue
            else: 
               logger.info(f"*** begin time okay, month {fileDesc['month']}")
            logger.info(f"*** , {fileDesc['timeEndExpected']}, {fileDesc['timeEnd']}")

            if fileDesc['timeEndExpected'] != (fileDesc['timeEnd']):
                logger.error(f"*** error with end time, month {fileDesc['month']}")
                errorInChekPeriods = True
            else:
                logger.info(f"*** end time okay, month {fileDesc['month']}")
        if (errorInChekPeriods):
            raise Exception("Error in method checkPeriods")
        pass
        

    
    # Lesen und  konvertieren des Sheets 0
    def convertFileV2(self, xlsxFile: str, csvFile: str):
        #print('\nMethod: convertFileV2')
        #print("xlsx-File=" + xlsxFile)
        #print("csv-File=" + csvFile)
        workbook = Workbook()
        workbook.LoadFromFile(xlsxFile)
        sheet = workbook.Worksheets[0]
        # sheet.SaveToFile(csvFile, ";", Encoding.get_UTF8())
        sheet.SaveToFile(csvFile, ";", )

    # Hier darf es nur ein Sheet geben,aber man kann Zeilen
    # am Beginn weglassen!
    def convertFileV1(self, xlsxFile: str, csvFile: str, skiprows=None):
        # print('\nMethod: convertFileV1')
        logger.info("xlsx-File=" + xlsxFile)
        logger.info("csv-File=" + csvFile)
        read_file = pd.read_excel(xlsxFile, skiprows=skiprows)
        #pd.read_excel(xlsxFile)
        read_file.to_csv(csvFile, index=None, header=True, sep=';')

    """
    Methode createPart1
    Parameter:
        strfilein:Name der Übersichtsdatei, hier "Uebersicht-2024-02-03.csv"
        strfileout: Datei, welche den erten Teil der Ausgaben enthält, hier "part1.csv"
        Rückgabewert: -
    Beide Dateien werden gleichzeitig geöffnet, einegelesen und eine geschriebn.
    Der Trennmechanismus ist noch nicht endgültig, da gilt auch für den zweiten Teil
    """

    def edaPart1(self, strfilein: str, strfileout: str):
        # print('\nMethod: edaPart1')
        logger.info("strfilein=" + strfilein)
        logger.info("strfileout=" + strfileout)

        i = 0
        with open(strfilein, mode='r') as filein:
            with open(strfileout, mode='w') as fileout:
                for line in filein:
                    i = i + 1
                    #print(i, line, end='')
                    if (i > 1 and i < 4): # Zeilemobergrenze von 5 auf 4 gesetzt
                        pass
                        print(line, file=fileout, end='')

        with open(strfileout, mode='r') as filedebug:
            for line in filedebug:
                pass
                #print(line, end='')

    """
    Methode createPart2
    Parameter:
        strfilein:Name der Übersichtsdatei, hier "Uebersicht-2024-02-03.csv"
        strfileout: Datei, welche den zweiten Teil der Ausgaben enthält, hier "part2.csv"
        Rückgabewert: -
    Beide Dateien werden gleichzeitig geöffnet, eine gelesen und eine geschriebn.
    Der Trennmechanismus ist noch nicht endgültig, so wie für den ersten Teil zweiten Teil.
    Zum Schluss wird die Ausagabedatei zu Testzwecken nochmals durgegangen und ausgegeben. 
    """

    def edaPart2(self, strfilein: str, strfileout: str):
        # print('\n### Method: edaPart2')
        logger.info("strfilein=" + strfilein)
        logger.info("strfileout=" + strfileout)

        i = 0
        with open(strfilein, mode='r') as filein:
            with open(strfileout, mode='w') as fileout:
                for line in filein:
                    i = i + 1
                    # print(i, line, end='')
                    if (i > 4 and i < 15): #erste Zeie wurde von 7 auf 4 geändert
                        pass
                        print(line, file=fileout, end='')

        with open(strfileout, mode='r') as filedebug:
            for line in filedebug:
                pass
                #print(line, end='')

    """
    Methode readEda1
        strfile: der Name des generierten ersten Teils, hir "part1.csv"
        return: -
        Es wird hauptsächlich der Beginn und das Ende der Messspanne gelesen (genau auf Viertelstunden
        Die Daten werden nicht weiterverfolgt. Die ersten Methoden sind hauptsächlich zu Übungszwecken 
        gedacht.     
    """

    def readEda1(self, fileDesc):
        # def readEda1(self, strfile):
        # print('\n### Method: readEda1')
        logger.info("strfile=" + fileDesc['edaPart1'])

        with open(fileDesc['edaPart1'], newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                print(row['Zeitraum von'], row['Zeitraum bis'], '\n')
                structTime = time.strptime(row['Zeitraum von'], '%Y-%m-%d %H:%M:%S')
                fileDesc['timeBegin'] = self.gd.structTime_TO_dateTime(structTime)
                print(fileDesc['timeBegin'])
                structTime = time.strptime(row['Zeitraum bis'], '%Y-%m-%d %H:%M:%S')
                fileDesc['timeEnd'] = self.gd.structTime_TO_dateTime(structTime)
                print(fileDesc['timeEnd'])
                pass

    """
    Methode readEda2
        strfile: der Name des generierten zweiten Teils, hier "part2.csv"
        return: Eindictionarymit den Daten
        Hier werden all zur EEG gehörigenZählpunkte protokolliert. Es wird  nur des Gesamtverbrauch bzw. 
        die Gesamteinspeisung protokolliert. Die Daten werden eingelsen und gut ersichtlich protokolliert. 
        Eindictionary itden wesentlichen Daten wird zurückgegebn.    
    """

    def readEda2(self, strfile):
        #print('\n### Method: readEda2')
        logger.info("strfile=" + strfile)

        self.gd.summeVerbrauch = 0
        self.gd.summeVerbrauchExists = False
        self.gd.summeLieferung = 0
        self.gd.summeLieferungExists = False
        self.gd.summePreisBrutto = 0
        self.gd.summePreisBruttoExists = False

        # with open(strfile, newline='') as csvfile:
        # with open(strfile, newline='' """encoding='utf-8' """ ) as csvfile:
        with open(strfile, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            res = []
            for row in reader:
                if row[Configuration.rowstr[1]] == 'CONSUMPTION':
                    x = row[Configuration.rowstr[3]]
                    y = float(x.replace(' ', '').replace(',', '.'))
                    row['Verbrauch'] = float(x.replace(' ', '').replace(',', '.'))
                    row['VerbrauchText']='{verbrauch: >8.2f}'.format(verbrauch=y)
                    z = y * 0.12
                    row['preisBrutto'] = z
                    row['preisBruttoText'] = '{verbrauch: >8.2f}'.format(verbrauch=z)
                    baseString = '{zaehlpunkt: <35}{type: <20}{lieferung: >15s}{verbrauch: >15.6f}'
                    # self.gd.summeVerbrauch += y
                    # self.gd.summeVerbrauchExists = True
                    # self.gd.summePreisBrutto += z
                    # self.gd.summePreisBruttoExists = True
                elif row[Configuration.rowstr[1]] == 'GENERATION':
                    y = row[Configuration.rowstr[4]]
                    y = float(y.replace(' ', '').replace(',', '.'))
                    x = row[Configuration.rowstr[2]]
                    x = float(x.replace(' ', '').replace(',', '.'))
                    x1 = y -x
                    row['Lieferung'] = x1
                    row['LieferungText'] = "{Lieferung:>8.2f}".format(Lieferung=x1)
                    # self.gd.summeLieferung += x1
                    # self.gd.summeLieferungExists = True
                    z = x1 * 0.12
                    row['preisBrutto'] = z
                    row['preisBruttoText'] = '{verbrauch: >8.2f}'.format(verbrauch=z)
                    # self.gd.summePreisBrutto += z
                    # self.gd.summePreisBruttoExists = True
                    #summeLieferung += interm['Lieferung']
                baseString = '{zaehlpunkt: <35}{type: <20}{lieferung: >15.6f}{verbrauch: >15s}'

                logger.info(f"{row['Zählpunkt']}, {row['Energierichtung']}, " + 
                      f"{row['Gesamte gemeinschaftliche Erzeugung [KWH]']}," +  # Spalte "K"
                      f"{row['Eigendeckung gemeinschaftliche Erzeugung [KWH]']}," +  # Spalte "I" Verbrauch
                      f"{row['Restüberschuss bei EG und je ZP [KWH]']}"  # Spalte "N"
                      )
                res.append(row)
                self.gd.addEdaElem(row)
            print()
            return res

    def createPrivate(self, csvFile: str):
        logger.info("strfile=" + csvfile)
        #data = open(template).read()
        #p = pathlib.Path(invoiceDir)
        #if not p.exists():
        #   p.mkdir()
        with (open(csvFile, newline='') as csvfile):
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                if row['Folgezeile'] == "":
                    lastMainZp = row['Zählpunkt']
                    self.gd.addPrivateElem(row)
                elif row['Folgezeile'] == "F":
                    zp2 = row['Zählpunkt']
                    # da dürfte noch ein Fehler sein!
                    self.gd.addZaehlpunkt(lastMainZp, zp2)

        #in dernzweiten Runde werden nur die Rabatte gesetzt (keine
        # Vorwärtreferenzen auf noch nicht eingetragene Zählpunkte mehr
        with (open(csvFile, newline='') as csvfile):
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                if row['Folgezeile'] == "":
                    lastMainZp = row['Zählpunkt']
                elif row['Folgezeile'] == "R":
                    row['mainZp'] = lastMainZp
                    self.gd.addRabatt3(row['Rabatt-Zaehlernummer'], lastMainZp, row)
                    #self.gd.addRabatt(row)

    def ermittleRechnungsSummen2(self):

        for privateElem in self.gd.privateList:
            summeVerbrauch = 0
            summeLieferung = 0
            summePreisBrutto = 0
            summeVerbrauchExists = False
            summeLieferungExists = False
            summePreisBruttoExists = False
            for edaElem in privateElem['edaListeNehmer']:
                if 'Verbrauch' in edaElem:
                    summeVerbrauch += edaElem['Verbrauch']
                    summeVerbrauchExists = True
                #if 'Lieferung' in edaElem:
                #    summeLieferung += edaElem['Lieferung']
                #    summeLieferungExists = True
                if 'preisBrutto' in edaElem:
                    summePreisBrutto += edaElem['preisBrutto']
                    summePreisBruttoExists = True
                pass
            for edaElem in privateElem['edaListeGeber']:
                if 'Lieferung' in edaElem:
                    summeLieferung += edaElem['Lieferung']
                    summeLieferungExists = True
                if 'preisBrutto' in edaElem:
                    summePreisBrutto += edaElem['preisBrutto']
                    summePreisBruttoExists = True
                pass
            sv1 = 0
            sv2 = 0
            if 'rabattGeber' in privateElem:
                for rabattElem in privateElem['rabattGeber']:
                    print('*** rabatt-Geber: ', len(privateElem['rabattGeber']))
                    sv1 += rabattElem['Verbrauch']
                    summeVerbrauch += rabattElem['Verbrauch']
                    summeVerbrauchExists = True
                    sv2 += rabattElem['preisBrutto']
                    summePreisBrutto += rabattElem['preisBrutto']
                    summePreisBruttoExists = True
            pass
            if 'rabattNehmer' in privateElem:
                for rabattElem in privateElem['rabattNehmer']:
                    print('*** rabatt-Geber: ', len(privateElem['rabattNehmer']))
                    sv1 += rabattElem['Verbrauch']  #!!!
                    summeLieferung += rabattElem['Verbrauch'] #!!!
                    summeLieferungxists = True
                    sv2 += rabattElem['preisBrutto']
                    summePreisBrutto += rabattElem['preisBrutto']
                    summePreisBruttoExists = True
            pass
            if summeVerbrauchExists==True:
                privateElem['summeVerbrauchExists'] = True
                privateElem['summeVerbrauch'] = summeVerbrauch
                privateElem['summeVerbrauchText'] = \
                    "{summeVerbrauch:>8.2f}".format(summeVerbrauch=summeVerbrauch)
            else:
                privateElem['summeVerbrauchText'] = ' '
            if summeLieferungExists==True:
                privateElem['summeLieferungExists'] = True
                privateElem['summeLieferung'] = summeLieferung
                privateElem['summeLieferungText'] = \
                    "{summeLieferung:>8.2f}".format(summeLieferung=summeLieferung)
            else:
                privateElem['summeLieferungText'] = ' '
            if summePreisBruttoExists==True:
                privateElem['summePreisBruttoExists'] = True
                privateElem['summePreisBrutto'] = summeLieferung
                privateElem['summePreisBruttoText'] = \
                    "{summePreisBrutto:>8.2f}".format(summePreisBrutto=summePreisBrutto)
            else:
                privateElem['summePreisBruttoText'] = ' '


    def ermittleRechnungsSummen(self):
        print("\n*** ermittleRechnungsSummen")
        for privateElem in self.gd.privateList:
            summeVerbrauch = 0
            summeLieferung = 0
            summePreisBrutto = 0
            summeVerbrauchExists = False
            summeLieferungExists = False
            summePreisBruttoExists = False

            for x in privateElem['edaData']:
                if 'Verbrauch' in x:
                    summeVerbrauch += x['Verbrauch']
                    summeVerbrauchExists = True
                if 'Lieferung' in x:
                    summeLieferung += x['Lieferung']
                    summeLieferungExists = True
                if 'preisBrutto' in x:
                    summePreisBrutto += x['preisBrutto']
                    summePreisBruttoExists = True
            pass
            sva = summeVerbrauch
            sla = summeLieferung
            spa = summePreisBrutto
            print(f"sva ={sva}, sla = {sla}, spa = {spa}")
            sl = 0
            if 'rabattGeber' in privateElem:
                for x in privateElem['rabattGeber']:
                   print('*** rabatt-Geber: ', x)
                   if 'Verbrauch' in x:
                       #summeLieferung -= x['Lieferung']
                       sl = sl + x['Verbrauch']
                       summeVerbrauchExists = True
                   pass
            sv = 0
            if 'rabattNehmer' in privateElem:
                for rabattElem in privateElem['rabattNehmer']:
                    print('*** rabatt-Elem: ', list(rabattElem.keys()))
                    #print(list(rabattElem.items()))
                    #for y in list(rabattElem.keys()):
                    #    print(list(rabattElem[y].items()))
                        #for xy in list(rabattElem[y].items()):
                            #if xy[0] =='Lieferung':
                        #    print(xy)

                    if 'Verbrauch' in x:
                        #summeVerbrauch += x['Verbrauch']
                        sv = sv + x['Verbrauch']
                        summeVerbrauchExists = True
                    pass

            if summeVerbrauchExists==True:
                privateElem['summeVerbrauchExists'] = True
                privateElem['summeVerbrauch'] = summeVerbrauch
                privateElem['summeVerbrauchText'] = "{summeVerbrauch:>8.2f}".format(summeVerbrauch=summeVerbrauch)
            else:
                privateElem['summeVerbrauchText'] = ' '
            if summeLieferungExists==True:
                privateElem['summeLieferungExists'] = True
                privateElem['summeLieferung'] = summeLieferung
                privateElem['summeLieferungText'] = "{summeLieferung:>8.2f}".format(summeLieferung=summeLieferung)
            else:
                privateElem['summeLieferungText'] = ' '
            if summePreisBruttoExists==True:
                privateElem['summePreisBruttoExists'] = True
                privateElem['summePreisBrutto'] = summeLieferung
                privateElem['summePreisBruttoText'] = "{summePreisBrutto:>8.2f}".format(summePreisBrutto=summePreisBrutto)
            else:
                privateElem['summePreisBruttoText'] = ' '

    def createHtmlInvoice(self):
        """
        Hier beginn die HTML Erzeugung mit jinja
        """

        for privateElem in self.gd.privateList:

            fileName = self.config.interm +\
                f"/{privateElem['Name'].lower()}_{privateElem['Vorname'].lower()}.html"
            edaListeGeber = privateElem['edaListeGeber']
            edaListeNehmer = privateElem['edaListeNehmer']
            edaListeGeberFlag = privateElem['edaListeGeberFlag']
            edaListeNehmerFlag = privateElem['edaListeNehmerFlag']
            #if 'edaData' in privateElem:
            #    edaData = privateElem['edaData']
            #else:
            #    edaData = []

            if 'rabattGeber' in privateElem:
                rabattGeber = privateElem['rabattGeber']
            else:
                rabattGeber = []
            if 'rabattNehmer' in privateElem:
                rabattNehmer = privateElem['rabattNehmer']
            else:
                rabattNehmer = []

            #if self.gd.summeVerbrauchExists==True:
            #    summeVerbrauchText="{summeVerbrauch:>8.2f}".format(summeVerbrauch=self.gd.summeVerbrauch)

            #else:
            #    summeVerbrauchText = ' '
            # print('!!!!?', summeVerbrauchText)
            #row['LieferungText'] = "{Lieferung:>8.2f}".format(Lieferung=summeLieferung)
            content = self.template.render(privateElem)
            with open(fileName, mode="w", encoding="utf-8") as message:
                message.write(content)
                print(f"...wrote {fileName}")

    def url_to_pdf(self, url, output_path):
        res = weasyprint.HTML(url).write_pdf(output_path)
        print(f"...wrote {output_path}")
        # print(res)

    def createPDFInvoice(self):
        for privateElem in self.gd.privateList:
            fileNameIn = self.config.interm +\
                f"/{privateElem['Name'].lower()}_{privateElem['Vorname'].lower()}.html"
            fileNameOut = self.config.resultDir +\
                f"/{privateElem['Name'].lower()}_{privateElem['Vorname'].lower()}.pdf"
            self.url_to_pdf(fileNameIn, fileNameOut)


    # das Hauptprogramm, im Moment fast alles in Kommentar
    def invoiceGeneration(self):
        # Hier werden bei Bedarf fehlene Ausgabe-directories erzeugt
        self.config.createBasicDirectories()
        # Ausgeben der allgemeinen Konfigurationsdaten
        self.config.printAll()
        #Eintragen (in GenerationData) und Prüfen der eda-Files  und ausgeben
        self.checkEdaFiles()
        # Migliederliste in csv-Formt umwandeln
        self.convertFileV1(self.config.mitgliederXlsx, self.config.mitgliederCsv, [0, 1])
        for list in self.gd.edaFileList:
            self.convertFileV1(list['fileName'], list['ueberSicht'])
            #self.convertFileV1(self.gd.edaFileList[0]['fileName'], self.gd.edaFileList[0]['ueberSicht'])
            self.edaPart1(list['ueberSicht'], list['edaPart1'])
            self.edaPart2(list['ueberSicht'], list['edaPart2'])
            self.readEda1(list)
            self.readEda2(list['edaPart2'])
            pass
        self.checkPeriods(self.gd.edaFileList)
        #self.edaPart2(self.config.edaUebersicht, self.config.edaPart2)
        #self.readEda1(self.config.edaPart1)
        #self.readEda2(self.config.edaPart2)
        #self.createPrivate(self.config.mitgliederCsv)
        #self.ermittleRechnungsSummen2()
        #self.createHtmlInvoice()
        #self.createPDFInvoice()


# ursprüngliche Version
# Startpunkt Programm invgen2.py
# Logger starten
logger = invlog.loggerTest()
logger.info("Here is invgen!")
# - Initialisierung von Configuration (befüllt) und GenerationData (zunächst leer) 
ig = InvoiceGeneration()
# - Hier läuft das Hauptprogramm, soweit es nicht kommentiert ist
ig.invoiceGeneration()
logger.info("Finishing invgen now...")
#print(ig.config.dataDir)
#ig.config.printAll()
#ig.gd.addPrivateElem({"abc": 17})
#ig.gd.addPrivateElem({"Zählpunkt": "BBB"})




#html.unescape()
#ig.gd.printAll()

# config = Configuration()
# config.printAll()
logger.info("Byby world!")