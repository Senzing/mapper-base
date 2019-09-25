import os
import sys
import argparse
import json
import re
from datetime import datetime
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
        try: self.mapping_standards = json.load(open(mappingStandardsFile,'r', encoding='latin-1'))
        except json.decoder.JSONDecodeError as err:
            print('')
            print('JSON error %s in %s' % (err, mappingStandardsFile))
            print('')
            self.initialized = False
        else:

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

            if 'ATTRIBUTE_CATEGORIES' not in self.mapping_standards:
                self.mapping_standards['ATTRIBUTE_CATEGORIES'] = {}
            if 'DOB' not in self.mapping_standards['ATTRIBUTE_CATEGORIES']:
                self.mapping_standards['ATTRIBUTE_CATEGORIES']['DOB'] = []
            if 'COUNTRY' not in self.mapping_standards['ATTRIBUTE_CATEGORIES']:
                self.mapping_standards['ATTRIBUTE_CATEGORIES']['COUNTRY'] = []
            if 'STATE' not in self.mapping_standards['ATTRIBUTE_CATEGORIES']:
                self.mapping_standards['ATTRIBUTE_CATEGORIES']['STATE'] = []
            if 'GROUP_NAME' not in self.mapping_standards['ATTRIBUTE_CATEGORIES']:
                self.mapping_standards['ATTRIBUTE_CATEGORIES']['GROUP_NAME'] = []
            if 'GROUP_ID' not in self.mapping_standards['ATTRIBUTE_CATEGORIES']:
                self.mapping_standards['ATTRIBUTE_CATEGORIES']['GROUP_ID'] = []

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
    def makeNameKey(self, nameString, entityType = 'UNKNOWN'):
        if not nameString:
            return ''

        #--remove strings bounded by parens or quotes
        if entityType == 'PERSON':
            originalName = nameString
            for boundExpression in re.findall('\(.*?\)', nameString):
                nameString = nameString.replace(boundExpression, " ")
            for boundExpression in re.findall('\".*?\"', nameString):
                nameString = nameString.replace(boundExpression, " ")
            #--if nothing left, just strip the parens or quotes
            if not nameString:
                nameString = originalName.replace("\"", "").replace("(", "").replace(")", "")

        #--remove puncuation and make upper case
        nameString = re.sub(r'[^\w\s]','', nameString).upper()

        #--remove any unwanted organization and person tokens
        tokens1 = nameString.split()
        tokens2 = []
        for token in tokens1:

            #--compress consecutive inititials for organizations
            if entityType == 'ORGANIZATION' and len(token) == 1 and tokens2 and tokens2 and len(tokens2[-1]) == 1: 
                tokens2[-1] += token
                if tokens2[-1] in self.mapping_standards['ORGANIZATION_TOKENS']: #--did it beome s.a.
                    if self.mapping_standards['ORGANIZATION_TOKENS'][tokens2[-1]]:  #--replace or skip
                        token = self.mapping_standards['ORGANIZATION_TOKENS'][tokens2[-1]]
                    else:
                        del tokens2[-1]
                continue

            #--no numerical tokens for people
            if entityType == 'PERSON' and any(char.isdigit() for char in token): 
                continue

            #--standardize or reject known organization tokens
            elif entityType in ('ORGANIZATION', 'UNKNOWN') and token in self.mapping_standards['ORGANIZATION_TOKENS']:
                if self.mapping_standards['ORGANIZATION_TOKENS'][token]:  #--replace or skip
                    token = self.mapping_standards['ORGANIZATION_TOKENS'][token]
                else:
                    continue

            #--standardize or reject known person tokens
            elif entityType in ('PERSON', 'UNKNOWN') and token in self.mapping_standards['PERSON_TOKENS']:
                if self.mapping_standards['PERSON_TOKENS'][token]:  #--replace or skip
                    token = self.mapping_standards['PERSON_TOKENS'][token]
                else:
                    continue

            #--add if not rejected
            tokens2.append(token)

        #--use all tokens if none left
        if not tokens2:  
            tokens2 = tokens1

        return '-'.join(sorted(tokens2))

    #----------------------------------------
    def attributeCategory(self, segment, attrName):
        if not segment[attrName]: #--no value
            return None

        #--clean it up
        try: 
            segment[attrName] = str(segment[attrName]).strip().upper()
            if segment[attrName] in self.mapping_standards['BAD_VALUES']:
                self.updateStat('BAD_VALUE', segment[attrName])
                return 'bad_Value', ''
        except: pass

        #--categorize it
        if 'NAME_ORG' in attrName:
            self.updateStat('NAME', 'ORG_NAME')
            return ('ORG_NAME', segment[attrName])
        elif 'NAME_FULL' in attrName:
            self.updateStat('NAME', 'FULL_NAME')
            return ('FULL_NAME', segment[attrName])
        elif 'NAME_LAST' in attrName:
            self.updateStat('NAME', 'PARSED_NAME')
            if attrName == 'NAME_LAST':
                prefix = ''
                suffix = ''
            elif attrName.endswith('NAME_LAST'):
                prefix = attrName.replace('NAME_LAST', '')
                suffix = ''
            else:
                suffix = attrName.replace('NAME_LAST', '')
                prefix = ''
            personName = segment[attrName] + ' '
            personName += segment[prefix+'NAME_FIRST'+suffix] + ' ' if prefix+'NAME_FIRST'+suffix in segment else ''
            personName += segment[prefix+'NAME_MIDDLE'+suffix] + ' ' if prefix+'NAME_MIDDLE'+suffix in segment else ''
            return ('PARSED_NAME', personName.strip())

        elif attrInList(attrName, self.mapping_standards['ATTRIBUTE_CATEGORIES']['STATE']):
            self.updateStat('STATE', attrName)
            if len(segment[attrName]) == 2:
                return ('STATE', segment[attrName])
            else:
                stateCode = self.isoStateCode(segment[attrName])
                if stateCode:
                    return ('STATE', stateCode)
                else: 
                    stateCode = self.isoCountryCode(segment[attrName])
                    if stateCode:
                        return ('STATE', stateCode)
            self.updateStat('STATE', 'missing', segment[attrName])

        elif attrInList(attrName, self.mapping_standards['ATTRIBUTE_CATEGORIES']['COUNTRY']):
            self.updateStat('COUNTRY', attrName)
            countryCode = self.isoCountryCode(segment[attrName])
            if countryCode:
                return ('COUNTRY', countryCode)
            self.updateStat('COUNTRY', 'missing', segment[attrName])

        elif attrInList(attrName, self.mapping_standards['ATTRIBUTE_CATEGORIES']['DOB']):
            self.updateStat('DOB', attrName)
            formattedDate = self.formatDate(segment[attrName])
            if formattedDate:
                return ('DOB', formattedDate)
            self.updateStat('DOB', 'BAD!', segment[attrName])

        elif attrInList(attrName, self.mapping_standards['ATTRIBUTE_CATEGORIES']['GROUP_NAME']):
            self.updateStat('GROUP_NAME', attrName)
            return ('GROUP_NAME', segment[attrName])

        elif attrInList(attrName, self.mapping_standards['ATTRIBUTE_CATEGORIES']['GROUP_ID']):
            self.updateStat('GROUP_ID', attrName)
            return ('GROUP_ID', segment[attrName])

        return None

    #----------------------------------------
    def jsonUpdater(self, jsonString):
        if type(jsonString) == dict:
            jsonData = jsonString
        else:
            try: jsonData = json.loads(jsonString)
            except json.decoder.JSONDecodeError as err:
                print('JSON error %s in %s' % (err, jsonString))
                return jsonString

        jsonData = self.dictKeysUpper(jsonData)
        categoryLists = {}        

        #--find all the sublists
        subListAttrs = []
        for attrName in jsonData:
            if type(jsonData[attrName]) == list:
                subListAttrs.append(attrName)

        #--process root level attributes
        for attrName in jsonData:
            if type(jsonData[attrName]) not in (list, dict):
                categoryValue = self.attributeCategory(jsonData, attrName)
                if categoryValue:
                    jsonData[attrName] = categoryValue[1]
                    if categoryValue[0] not in categoryLists:
                        categoryLists[categoryValue[0]] = []
                    categoryLists[categoryValue[0]].append(categoryValue[1])

        #--process sub list attributes
        for subListAttr in subListAttrs:
            for i in range(len(jsonData[subListAttr])):
                jsonData[subListAttr][i] = self.dictKeysUpper(jsonData[subListAttr][i])
                for attrName in jsonData[subListAttr][i]:
                    if type(jsonData[subListAttr][i][attrName]) not in (list, dict):
                        categoryValue = self.attributeCategory(jsonData[subListAttr][i], attrName)
                        if categoryValue:
                            jsonData[subListAttr][i][attrName] = categoryValue[1]
                            if categoryValue[0] not in categoryLists:
                                categoryLists[categoryValue[0]] = []
                            categoryLists[categoryValue[0]].append(categoryValue[1])

        #--determine record type if not expressly stated
        if 'RECORD_TYPE' in jsonData and jsonData['RECORD_TYPE'] in ('ORGANIZATION', 'PERSON'):
            pass
        else:
            jsonData['RECORD_TYPE'] = 'PERSON'
            if 'ENTITY_TYPE' in jsonData and jsonData['ENTITY_TYPE'] in ('ORGANIZATION', 'PERSON'):
                jsonData['RECORD_TYPE'] = jsonData['ENTITY_TYPE']
            elif 'ORG_NAME' in categoryLists:
                jsonData['RECORD_TYPE'] = 'ORGANIZATION'
            elif 'FULL_NAME' in categoryLists:
                for fullName in categoryLists['FULL_NAME']:
                    if self.isCompanyName(fullName):                
                        jsonData['RECORD_TYPE'] = 'ORGANIZATION'
        self.updateStat('RECORD_TYPE', jsonData['RECORD_TYPE'])

        #--prepare for key generation
        nameList1 = categoryLists['ORG_NAME'] if 'ORG_NAME' in categoryLists else []
        nameList2 = categoryLists['FULL_NAME'] if 'FULL_NAME' in categoryLists else []
        nameList3 = categoryLists['PARSED_NAME'] if 'PARSED_NAME' in categoryLists else []
        nameList = set(nameList1 + nameList2 + nameList3)
        stateList = set(categoryLists['STATE']) if 'STATE' in categoryLists else []
        countryList = set(categoryLists['COUNTRY']) if 'COUNTRY' in categoryLists else []
        dobList = set(categoryLists['DOB']) if 'DOB' in categoryLists else []
        groupNameList = set(categoryLists['GROUP_NAME']) if 'GROUP_NAME' in categoryLists else []
        groupIdList = set(categoryLists['GROUP_ID']) if 'GROUP_ID' in categoryLists else []

        #--add state list to country list
        countryList = list(countryList)
        for stateCode in stateList:
            if len(stateCode) == 2:
                countryList.append('US-' + stateCode)
            else:
                countryList.append(stateCode)

        #--add country codes
        thisList = []
        for countryCode in countryList:
            thisList.append({'ISO_COUNTRY_CODE': countryCode})
        if thisList: 
            if len(thisList) == 1:
                jsonData.update(thisList[0])
            else:
                jsonData['ISO_COUNTRIES'] = thisList

        #--add composite keys
        if countryList or dobList or groupNameList or groupIdList:
            thisList = []
            for nameFull in nameList:
                nameKey = self.makeNameKey(nameFull, jsonData['RECORD_TYPE'])
                for dobKey in dobList:
                    self.updateStat('COMPOSITE_KEY', 'CK_NAME_DOB')
                    thisList.append({'CK_NAME_DOB': nameKey + '|' + dobKey})
                    for cntryKey in countryList:
                        self.updateStat('COMPOSITE_KEY', 'CK_NAME_DOB_COUNTRY')
                        thisList.append({'CK_NAME_DOB_COUNTRY': nameKey + '|' + dobKey + '|' + cntryKey})
                for cntryKey in countryList:
                    self.updateStat('COMPOSITE_KEY', 'CK_NAME_COUNTRY')
                    thisList.append({'CK_NAME_COUNTRY': nameKey + '|' + cntryKey})
                for groupName in groupNameList:
                    groupNameKey = self.makeNameKey(groupName, 'ORGANIZATION')
                    self.updateStat('COMPOSITE_KEY', 'CK_NAME_GROUPNAME')
                    thisList.append({'CK_NAME_GROUPNAME': nameKey + '|' + groupNameKey})
                for groupIdKey in groupIdList:
                    self.updateStat('COMPOSITE_KEY', 'CK_NAME_GROUPID')
                    thisList.append({'CK_NAME_GROUPID': nameKey + '|' + groupIdKey})
        if thisList: 
            jsonData['COMPOSITE_KEYS'] = thisList

        return jsonData

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

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-i', '--input_file', default=os.getenv('input_file', None), type=str, help='name of a json file to standardize.')
    argparser.add_argument('-o', '--output_file', default=os.getenv('output_file', None), type=str, help='name of file to write updated json output to.')
    argparser.add_argument('-l', '--log_file', default=os.getenv('log_file', None), type=str, help='optional statistics filename (json format).')
    args = argparser.parse_args()
    inputFileName = args.input_file
    outputFileName = args.output_file
    logFile = args.log_file
    
    #--test the instance
    baseLibrary = base_library(appPath + os.path.sep + 'base_variants.json')
    if baseLibrary.initialized:

        #--open input file if they gave one
        if inputFileName:

            if not os.path.exists(inputFileName):
                print('')
                print('File %s does not exist!' % inputFileName)
                print('')
            else:

                #--open output file
                if outputFileName:
                    try: outputFileHandle = open(outputFileName, "w", encoding='utf-8')
                    except IOError as err:
                        print('')
                        print('Could not open output file %s for writing' % outputFileName)
                        print(' %s' % err)
                        print('')
                        sys.exit(1)

                print('')
                lineCnt = 0
                with open(inputFileName, 'r') as f:
                    for line in f:
                        if len(line.strip()) > 0:
                            lineCnt += 1
                            jsonData = baseLibrary.jsonUpdater(line)
                            if not jsonData:
                                shutDown = True

                            if not outputFileName:
                                print(json.dumps(jsonData, indent=4, sort_keys=True))
                                pause()
                            else:
                                msg = json.dumps(jsonData)
                                try: outputFileHandle.write(msg + '\n')
                                except IOError as err:
                                    print('')
                                    print('Could not write to %s' % outputFileName)
                                    print(' %s' % err)
                                    print('')
                                    shutDown = True

                                if lineCnt % 1000 == 0:
                                    print('%s lines written' % lineCnt)

                        if shutDown:
                            break

                if outputFileName:
                    print('%s lines written, %s!' % (lineCnt, ('aborted' if shutDown else 'complete')))                                    
                    outputFileHandle.close()

                #--write statistics file
                if logFile: 
                    print('')
                    with open(logFile, 'w') as outfile:
                        json.dump(baseLibrary.statPack, outfile, indent=4, sort_keys = True)    
                    print('Mapping stats written to %s' % logFile)

                print('')
                elapsedMins = round((time.time() - procStartTime) / 60, 1)
                if shutDown == 0:
                    print('Process completed successfully in %s minutes!' % elapsedMins)
                else:
                    print('Process aborted after %s minutes!' % elapsedMins)
                print('')

    sys.exit()

