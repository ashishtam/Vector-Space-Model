# @author Ashish Tamrakar
# @Date 2016-03-07
# Program to find the inverted file of the Cransfield collection and use Vector Space Model to query
# Python v2.7.10
import re
from stemmer import PorterStemmer
import json


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

def main():
    # Reading the document from the file
    # file = open("cran.all.1400", "r")
    file = open("cran.txt", "r")
    documents = file.read()
    # Reading stop words from the file
    fileStopwords = open('stopwords.txt', 'r')
    stopwordsList = fileStopwords.read()
    stopwords = stopwordsList.split()
    # List that maintains the document id number, number of unique terms in document, for each term in the document, its term and it's term frequency.
    docId = 1

    #InvFileHash
    invFileHash = {}
    # Splits the multiple documents of the same file into list
    document = re.split(".I | \n.I", documents)[1:]

    for doc in enumerate(document):
        startIndex = doc[1].index('.W\n')
        text = doc[1][startIndex + 3:]
        words = re.findall(r'\w+', text)

        pObj = PorterStemmer()
        listWords = {}
        for word in words:
            flagStopwords = word.lower() in stopwords
            if (not flagStopwords and word.isalpha()):
                stemWord = pObj.stem(word, 0, len(word) - 1)
                listWords = addToDict(listWords, stemWord)

        docList = addDoc(docId, listWords)
        docId += 1
        invFileHash = createInvFileHash(invFileHash, docList)

    writeToFile(invFileHash)


main()