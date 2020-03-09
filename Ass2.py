import glob
import xml.etree.cElementTree as ET
from nltk import word_tokenize
from nltk import PorterStemmer
import math
from operator import itemgetter

# Getting the topics and their numbers
queryFile = open("queries.txt", "a+")

tree = ET.ElementTree(file='topics.xml')
root = tree.getroot()
for i in root:
    if i.tag == 'topic':
        # Write the number of that query
        queryFile.write(str(i.get('number')) + '  ')
        for query in i:
            if query.tag == 'query':
                # Write the query
                queryFile.write(str(query.text.lower()) + '\n')
queryFile.close()

wordsInCorpus = 0
wordsInEachDoc = {}

path = 'C:/Users/haide/PycharmProjects/Ass2/corpus2/*'
files = glob.glob(path)
for file in files:
    oneFileAtAtime = open(file, encoding='utf-8', errors='ignore')
    dataOfEachFile = oneFileAtAtime.read()
    dataOfEachFile = word_tokenize(dataOfEachFile)

    wordsInCorpus = wordsInCorpus + len(dataOfEachFile)
    wordsInEachDoc[files.index(file)] = len(dataOfEachFile)

# Computing Okapi BM25 and Dirichlet
stemmer = PorterStemmer()
avgLenD = wordsInCorpus / len(files)
scoreForDirichlet = 0

# Constants
mu = 1
b = 0.75
k1 = 1.2
k2 = 1

dirichletList = []
BMList = []
stemmedList = []

queryFile2 = open("queries.txt", "r", encoding='utf-8', errors="ignore")
allLines = queryFile2.readlines()

noOfFiles = len(files)
for line in allLines:
    # query loop
    strippedLine = line.strip()
    splittedLine = strippedLine.split()
    finalLine = splittedLine[1:]

    length = len(finalLine)

    for i in range(noOfFiles):
        # documents loop
        eachFile = open(files[i], errors='ignore')
        docData = eachFile.read()
        docData = word_tokenize(docData)
        docLength = len(docData)

        K = k1 * (1 - b) + (b * (int(docLength) / int(avgLenD)))
        for indax in range(length):
            # query loop, word by word
            wordInQuery = finalLine[indax]

            wordCountInQuery = finalLine.count(wordInQuery)
            stemmedWord = stemmer.stem(wordInQuery)

            wordCountInDoc = docData.count(wordInQuery)

            # this file has term frequencies of each file
            termFrequenciesFile = open("docTermFreqs.txt", "r")
            eachTermFreq = termFrequenciesFile.readlines()
            corpusUniqueCount = 0

            for iterator in eachTermFreq:
                splitTheLine = iterator.split()

                if splitTheLine[0] == wordInQuery:
                    corpusUniqueCount = splitTheLine[1]
                    break

            # BM25
            BMterm1 = math.log(docLength + 0.5 / float(int(corpusUniqueCount) + 0.5))
            BMterm2 = ((1 + k1) * wordCountInDoc) / (K + wordCountInDoc)
            BMterm3 = ((1 + k2) * wordCountInQuery) / (k2 + wordCountInQuery)
            BM25 = BMterm1 * BMterm2 * BMterm3
            BMList.append(BM25)

            # Dirichlet
            DirichletTerm1 = (docLength / (docLength + mu)) * (wordCountInDoc / docLength)
            DirichletTerm2 = mu / (mu + int(docLength)) * (int(corpusUniqueCount) / int(wordsInCorpus))
            scoreForDirichlet = DirichletTerm1 + DirichletTerm2
            dirichletList.append(scoreForDirichlet)

        scoreWithSummation = sum(dirichletList)
        dirichletFile = open("Dirichlet.txt", "a+", encoding='utf-8', errors="ignore")
        dirichletFile.write(str(splittedLine[0]) + "  " + str(files[i]) + "  " + str(scoreWithSummation) + "\n")

        BM25Total = sum(BMList)
        BM25File = open("BM25.txt", "a+", encoding='utf-8', errors="ignore")
        BM25File.write(str(splittedLine[0]) + "  " + str(files[i]) + "  " + str(BM25Total) + "\n")

        dirichletList.clear()
        BMList.clear()

BM25File = open("BM25.txt", "r")
contentOfBM25File = BM25File.readlines()

tempList = []

extraFile = open("FinaleBM25.txt", "a+", encoding='utf-8', errors="ignore")
x = 0

for line in contentOfBM25File:
    strippedLine = line.strip()
    splittedLine = strippedLine.split()
    finalLine = splittedLine

    tempList.append([finalLine[0], finalLine[1], finalLine[2]])
    x = x + 1
    if x == 4:
        tempList = sorted(tempList, key=itemgetter(2), reverse=True)
        x = 0
        i = 0
        for items in tempList:
            extraFile.write(str(tempList[i][0]) + "\t" + str(tempList[i][1]) + "\t" + str(tempList[i][2]) + "\n")
            i = i + 1
        tempList.clear()

extraFile.close()

DirichletFile = open("Dirichlet.txt", "r")
contentOfDirichletFile = DirichletFile.readlines()

tempList.clear()

extraFile2 = open("FinaleDirichlet.txt", "a+", encoding='utf-8', errors="ignore")
x = 0

for line in contentOfDirichletFile:
    strippedLine = line.strip()
    splittedLine = strippedLine.split()
    finalLine = splittedLine

    tempList.append([finalLine[0], finalLine[1], finalLine[2]])
    x = x + 1
    if x == 4:
        tempList = sorted(tempList, key=itemgetter(2), reverse=True)
        x = 0
        i = 0
        for items in tempList:
            extraFile2.write(str(tempList[i][0]) + "\t" + str(tempList[i][1]) + "\t" + str(tempList[i][2]) + "\n")
            i = i + 1
        tempList.clear()

extraFile2.close()
