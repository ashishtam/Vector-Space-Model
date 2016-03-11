# @author Ashish Tamrakar
# @Date 2016-03-07
# Program to find the inverted file of the Cransfield collection and use Vector Space Model to query
# Python v2.7.10
import re
from stemmer import PorterStemmer
import json
import math


def readFromFile(fileName, type):
    """
    Returns the content of the file.
    """
    file = open(fileName, type)
    fileContent = file.read()
    return fileContent


def addToDict(listWords, stemWord):
    """
    Returns the listWords frequency.
    """
    if (stemWord in listWords):
        listWords[stemWord] += 1
    else:
        listWords[stemWord] = 1
    return listWords


def addDoc(docId, listWords):
    """
    Return the dictionary with {id, unique terms, and terms containing its term and term frequency}
    """
    sortedList = sorted(listWords.items(), key=lambda t: t[0])
    output = {'id': docId, 'unique': len(sortedList), 'terms': sortedList}
    return output


def createInvFileHash(invFileHash, docList):
    """
    Creates/Updates the invFileHash from the documentList obtained.
    """
    id = docList['id']
    for term in docList['terms']:
        if (term):
            if (term[0] in invFileHash):
                invFileHash[term[0]][0] += 1
                invFileHash[term[0]][1].append([id, term[1]])
            else:
                invFileHash[term[0]] = [1, [[id, term[1]]]]
    return invFileHash


def writeToFile(invFileHash):
    """
    Writes to the file
    """
    with open('output.json', 'w') as f:
        json.dump(invFileHash, f)


def loadFromFile():
    """
    Loads the Inverted File Hash JSON file.
    """
    with open('output.json', 'r') as f:
        return json.load(f)


def calculateIDF(dic, total):
    """
    Calculate the IDF of each terms.
    """
    IDF = {}
    for item in dic:
        IDF[item] = {'freq': dic[item][0], 'idf': math.log(1 + total / dic[item][0]), 'docList': dic[item][1]}
    return IDF


def calculateTFList(dic):
    """
    Generates the TF list of each and every words
    """
    TF = {}
    for item in dic:
        TF[item] = []
        for data in dic[item][1]:
            TF[item].append([data[0], 1 + math.log(data[1])])
    return TF


def calculateWD(TF, totalDocument):
    """
    Calculates the Wd needed to calculated cosine measure.
    """
    WD = {}
    for docId in range(1, totalDocument + 1):
        tempWd = 0
        for item in TF:
            listItem = [x[0] for x in TF[item]]
            if (docId in listItem):
                indexDocId = listItem.index(docId)
                tempWd += math.pow(TF[item][indexDocId][1], 2)
        WD[docId] = math.sqrt(tempWd)
    return WD


def calculateSimilarity(processedQuery, IDF, WD, totalDocument):
    Sim = {}
    for docId in range(1, totalDocument + 1):
        temp = 0
        # To skip those documents that are blank
        if not WD[docId]:
            continue
        for item in processedQuery:
            if (item in IDF):
                listItem = [x[0] for x in IDF[item]['docList']]
                if docId in listItem:
                    indexDoc = listItem.index(docId)
                    freqDT = IDF[item]['docList'][indexDoc][1]
                    logFreqDT = 1 + math.log(freqDT)
                else:
                    logFreqDT = 0
                temp += logFreqDT * IDF[item]['idf']
            else:
                temp += 0
        if (temp):
            Sim[docId] = 1 / WD[docId] * temp

    sortedDocument, sortedRank = sorted(Sim, key=Sim.__getitem__, reverse=True), sorted(Sim.values(), reverse=True)
    return sortedDocument


def vectorSpaceModel(totalDocument, queryFileRead, stopwords):
    """
    Query to calculate the cosine similarity between document d and Query Q
    """

    # Loads the inverted File Hash
    dic = loadFromFile()
    #
    queryList = processQueryList(queryFileRead)
    # Calculation of Inverse Document Frequency
    IDF = calculateIDF(dic, totalDocument)
    # Calculation of Term Frequency
    TF = calculateTFList(dic)
    # Calculation of Wd from all the Term Frequency calculated
    WD = calculateWD(TF, totalDocument)

    pObj = PorterStemmer()
    fileWrite = open("outputdocument.txt", "w")
    for query in queryList:
        fileWrite.write("\n---------------------------------------------------------------------------------------")
        fileWrite.write("\nQuery: " + query)
        # Separate the string of query into list of words
        listQuery = re.findall(r'\w+', query)
        # Remove the stopwords and numbers from the list of query words
        queryWithoutStopword = [x for x in listQuery if x not in stopwords and x.isalpha()]
        # Stem the list of query words
        processedQuery = [pObj.stem(x.lower(), 0, len(x) - 1) for x in queryWithoutStopword]
        # Calculate the cosine measure (Similarity) for the query
        rankedDocList = calculateSimilarity(processedQuery, IDF, WD, totalDocument)
        fileWrite.write("\nTotal number of documents retrieved: " + str(len(rankedDocList)))
        fileWrite.write("\nDocument ID:\n")
        fileWrite.write(''.join(str(rankedDocList)))
        fileWrite.write("\n---------------------------------------------------------------------------------------")
    fileWrite.close()

    print "Writing to outputdocument.txt file completes."


def processQueryList(queryFileRead):
    """
    Returns the query read from the file into list form by separating on finding .I and then .W
    """
    queryLists = re.split(".I | \n.I", queryFileRead)[1:]
    queryList = []
    for query in enumerate(queryLists):
        startIndex = query[1].index('.W')
        text = query[1][startIndex + 3:]
        queryList.append(text)

    return queryList


def main():
    # Reading the document from the file
    fileName = "cran.all.1400"

    documents = readFromFile(fileName, "r")

    # Reading stop words from the file
    stopwordsList = readFromFile("stopwords.txt", "r")
    stopwords = stopwordsList.split()

    # List that maintains the document id number, number of unique terms in document, for each term in the document, its term and it's term frequency.
    docId = 1

    # InvFileHash
    invFileHash = {}

    # Splits the multiple documents of the same file into list
    document = re.split(".I | \n.I", documents)[1:]
    totalDocument = len(document)
    print "Total documents:", totalDocument
    for doc in enumerate(document):
        startIndex = doc[1].index('.W\n')
        text = doc[1][startIndex + 3:]
        words = re.findall(r'\w+', text)

        pObj = PorterStemmer()
        listWords = {}
        for word in words:
            flagStopwords = word.lower() in stopwords
            if (not flagStopwords and word.isalpha()):
                stemWord = pObj.stem(word.lower(), 0, len(word) - 1)
                listWords = addToDict(listWords, stemWord)

        docList = addDoc(docId, listWords)
        docId += 1
        invFileHash = createInvFileHash(invFileHash, docList)

    # Writes to the Inverted File Hash file
    writeToFile(invFileHash)

    # To read the queries list from the cran query file
    queryFileRead = readFromFile("cran.qry", "r")

    # Calculate the Vector Space Model (total number of documents, stopwords list)
    vectorSpaceModel(totalDocument, queryFileRead, stopwords)


main()
