# @author Ashish Tamrakar
# @Date 2016-03-07
# Program to find the inverted file of the Cransfield collection and use Vector Space Model to query
# Python v2.7.10
import re
from stemmer import PorterStemmer
import json
import math


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
        IDF[item] = {'freq': dic[item][0], 'idf': math.log(1 + total / dic[item][0])}
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
    Calculates the Wd needed to calculated cosine measure
    :param TF:
    :param totalDocument:
    :return:
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


def vectorSpaceModel(totalDocument):
    """
    Query to calculate the cosine similarity between document d and Query Q
    """
    dic = loadFromFile()
    IDF = calculateIDF(dic, totalDocument)
    TF = calculateTFList(dic)
    WD = calculateWD(TF, totalDocument)


def main():
    # Reading the document from the file
    # file = open("cran.all.1400", "r")
    file = open("test.txt", "r")
    # file = open("cran.txt", "r")
    documents = file.read()
    # Reading stop words from the file
    fileStopwords = open('stopwords.txt', 'r')
    stopwordsList = fileStopwords.read()
    stopwords = stopwordsList.split()
    # List that maintains the document id number, number of unique terms in document, for each term in the document, its term and it's term frequency.
    docId = 1

    # InvFileHash
    invFileHash = {}
    # Splits the multiple documents of the same file into list
    document = re.split(".I | \n.I", documents)[1:]
    totalDocument = len(document)
    print "Total document:", totalDocument
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

    writeToFile(invFileHash)
    vectorSpaceModel(totalDocument)


main()
