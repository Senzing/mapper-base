import os
import sys
import argparse
import json
import re
from datetime import datetime
import time
import signal
import random

#=========================
class base_library():

    #----------------------------------------
    def __init__(self, mappingStandardsFile, isoCountrySize = 3):
        self.initialized = True
        self.statPack = {}

        if not os.path.exists(mappingStandardsFile):
            print('')
            print('File %s is missing!' % mappingStandardsFile)
            print('')
            self.initialized = False
            return

        try: self.mapping_standards = json.load(open(mappingStandardsFile,'r', encoding='latin-1'))
        except json.decoder.JSONDecodeError as err:
            print('')
            print('JSON error %s in %s' % (err, mappingStandardsFile))
            print('')
            self.initialized = False
            return

        if 'ORGANIZATION_TOKENS' not in self.mapping_standards:
            self.mapping_standards['ORGANIZATION_TOKENS'] = {}
        if 'PERSON_TOKENS' not in self.mapping_standards:
            self.mapping_standards['PERSON_TOKENS'] = {}
        if 'STATE_CODES' not in self.mapping_standards:
            self.mapping_standards['STATE_CODES'] = {}
        if 'COUNTRY_CODES' not in self.mapping_standards:
            self.mapping_standards['COUNTRY_CODES'] = {}
        if 'BAD_VALUES' not in self.mapping_standards:
            self.mapping_standards['BAD_VALUES'] = {}

        #--supported date formats
        self.dateFormats = []
        self.dateFormats.append("%Y-%m-%d")
        self.dateFormats.append("%m/%d/%Y")
        self.dateFormats.append("%d/%m/%Y")
        self.dateFormats.append("%d-%b-%Y")
        self.dateFormats.append("%Y")
        self.dateFormats.append("%Y-%M")
        self.dateFormats.append("%m-%Y")
        self.dateFormats.append("%m/%Y")
        self.dateFormats.append("%b-%Y")
        self.dateFormats.append("%b/%Y")
        self.dateFormats.append("%m-%d")
        self.dateFormats.append("%m/%d")
        self.dateFormats.append("%b-%d")
        self.dateFormats.append("%b/%d")
        self.dateFormats.append("%d-%m")
        self.dateFormats.append("%d/%m")
        self.dateFormats.append("%d-%b")
        self.dateFormats.append("%d/%b")

        #--set iso country code size 
        if isoCountrySize not in (2, 3):
            print('')
            print('The ISO Country size must be 2 or 3.')
            print('')
            self.initialized = False
        self.isoCountrySize = 'ISO' + str(isoCountrySize)
    
    #----------------------------------------
    def formatDate(self, dateString, outputFormat = None):
        for dateFormat in self.dateFormats:
            try: dateValue = datetime.strptime(dateString, dateFormat)
            except: pass
            else: 
                if not outputFormat:
                    if len(dateString) == 4:
                        outputFormat = '%Y'
                    elif len(dateString) in (5,6):
                        outputFormat = '%m-%d'
                    elif len(dateString) in (7,8):
                        outputFormat = '%Y-%m'
                    else:
                        outputFormat = '%Y-%m-%d'
                return datetime.strftime(dateValue, outputFormat)
        return None

    #---------------------------------------
    def isoCountryCode(self, countryString):
        countryString = countryString.replace('.', '').upper()
        if countryString in self.mapping_standards['COUNTRY_CODES']:
            return self.mapping_standards['COUNTRY_CODES'][countryString.upper()][self.isoCountrySize]
        elif ',' in countryString:
            countryString = countryString[countryString.rfind(',')+1:].strip()
            if countryString in self.mapping_standards['COUNTRY_CODES']:
                return self.mapping_standards['COUNTRY_CODES'][countryString.upper()][self.isoCountrySize]

    #---------------------------------------
    def isoStateCode(self, stateString):
        if stateString.upper() in self.mapping_standards['STATE_CODES']:
            return self.mapping_standards['STATE_CODES'][stateString.upper()]

    #-----------------------------------
    def isCompanyName(self, nameString):
        if nameString:
            for token in nameString.lower().replace('.',' ').replace(',',' ').split():
                if token.upper() in self.mapping_standards['ORGANIZATION_TOKENS']:
                    return True
        return False

    #----------------------------------------
    def dictKeysUpper(self, jsonDataIn):
        return {k.upper():v for k,v in jsonDataIn.items()}

    #----------------------------------------
    def updateStat(self, cat1, cat2, example = None):
        if cat1 not in self.statPack:
            self.statPack[cat1] = {}
        if cat2 not in self.statPack[cat1]:
            self.statPack[cat1][cat2] = {}
            self.statPack[cat1][cat2]['count'] = 0

        self.statPack[cat1][cat2]['count'] += 1
        if example:
            if 'examples' not in self.statPack[cat1][cat2]:
                self.statPack[cat1][cat2]['examples'] = []
            if example not in self.statPack[cat1][cat2]['examples']:
                if len(self.statPack[cat1][cat2]['examples']) < 5:
                    self.statPack[cat1][cat2]['examples'].append(example)
                else:
                    randomSampleI = random.randint(2,4)
                    self.statPack[cat1][cat2]['examples'][randomSampleI] = example
        return

#----------------------------------------
def attrInList(jsonAttr, attrList):
    for attrName in attrList:
        if attrName in jsonAttr:
            return True
    return False

#----------------------------------------
def pause(question='PRESS ENTER TO CONTINUE ...'):
    """ pause for debug purposes """
    try: response = input(question)
    except KeyboardInterrupt:
        response = None
        global shutDown
        shutDown = True
    return response

#----------------------------------------
def signal_handler(signal, frame):
    print('USER INTERUPT! Shutting down ... (please wait)')
    global shutDown
    shutDown = True
    return

#----------------------------------------
if __name__ == "__main__":
    appPath = os.path.dirname(os.path.abspath(sys.argv[0]))

    global shutDown
    shutDown = False
    signal.signal(signal.SIGINT, signal_handler)
    procStartTime = time.time()
    progressInterval = 10000

    #--test the instance
    baseLibrary = base_library(appPath + os.path.sep + 'base_variants.json')
    if baseLibrary.initialized:
        print('')
        print('successfully initialized!')
        print('')

    sys.exit()

