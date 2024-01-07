import csv
#import pandas as pd
#from mlxtend.frequent_patterns  import association_rules
from collections import defaultdict
from itertools import chain, combinations
import math

MINSUP = 0.6
MINCONF = 0.6

class contingencyTable:
    data11 = 0
    data10 = 0
    data01 = 0
    data00 = 0
    data1X = 0
    dataX0 = 0
    dataX1 = 0
    data0X = 0
    dataXX = 0
    supp = 0
    CC = 0
    IS = 0

def readFromInputFile(fileName):
    # extract rows from csv file
    fileHandle = open(fileName, "r")
    for row in fileHandle:
        row = row.strip().rstrip(",")
        rowRecords = frozenset(row.split(","))
        yield rowRecords
        #print("rowRecords in csv file: ", rowRecords)

def getItemSetWithMinSup(itemSet, transactionList, MINSUP, frequencyOfItemSets, lengthIter):
    localCandidateItemSet = set()
    localSet = defaultdict(int)

    for item in itemSet:
        for transaction in transactionList:
            if item.issubset(transaction):
                frequencyOfItemSets[item] += 1
                localSet[item] += 1

    #print("localSet: ", localSet)

    # if item's frequency is bigger than support add to new set
    for item, count in localSet.items():
        support = float(count) / len(transactionList)
        #print("Item: ", item, " support: ", support)
        if support >= MINSUP:
            localCandidateItemSet.add(item)

    print("frequent ", lengthIter, "-itemSet: ", localCandidateItemSet)
    return localCandidateItemSet

def joinSet(itemSet, itemSetLength):
        return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == itemSetLength])

def getSubsets(arr):
    # Return non empty subsets of arr
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])

def extractItemSetAndTransactionList(rowRecords):
    transactionList = list()
    itemSet = set()
    
    for rowRecord in rowRecords:
        transaction = frozenset(rowRecord)
        transactionList.append(transaction)
        for item in transaction:
            if not ("T" in item):
                itemSet.add(frozenset([item]))

    #print("itemset: ", itemSet)
    #print("transactionList: ", transactionList)
    return itemSet, transactionList

def generateLargeItemSets(candidateItemSet):
    currentLargeItemSet = candidateItemSet
    lengthIter = 2 # start from 2-itemsets
    while (currentLargeItemSet != set([])):
        largeItemSets[lengthIter - 1] = currentLargeItemSet
        currentLargeItemSet = joinSet(currentLargeItemSet, lengthIter)

        tempItem=[]
        tempTables = {}
        for itemSet in currentLargeItemSet:
            for item in itemSet:
                tempItem.append(item)

            tempTables[lengthIter] = contingencyTable()
            for transaction in transactionList:
                if (tempItem[0] in transaction) and (tempItem[0+1] in transaction):
                    tempTables[lengthIter].data11 += 1
                elif (tempItem[0] in transaction) and (tempItem[0+1] not in transaction):
                    tempTables[lengthIter].data10 += 1
                elif (tempItem[0] not in transaction) and (tempItem[0+1] in transaction):
                    tempTables[lengthIter].data01 += 1
                elif (tempItem[0] not in transaction) and (tempItem[0+1] not in transaction):
                    tempTables[lengthIter].data00 += 1


            print("TABLE for:", itemSet)
            tempTables[lengthIter].data1X = tempTables[lengthIter].data11 + tempTables[lengthIter].data10
            tempTables[lengthIter].dataX0 = tempTables[lengthIter].data10 + tempTables[lengthIter].data00
            tempTables[lengthIter].dataX1 = tempTables[lengthIter].data11 + tempTables[lengthIter].data01 
            tempTables[lengthIter].data0X = tempTables[lengthIter].data01 + tempTables[lengthIter].data00
            tempTables[lengthIter].dataXX = tempTables[lengthIter].data1X + tempTables[lengthIter].data0X
            
            # calculate supp, CC, IS measures for each table
            tempTables[lengthIter].supp = tempTables[lengthIter].data11 / tempTables[lengthIter].dataXX
            #tempTables[lengthIter].CC = math.sqrt(tempTables[lengthIter].data0X * tempTables[lengthIter].data1X * tempTables[lengthIter].dataX1 * tempTables[lengthIter].dataX0) if (tempTables[lengthIter].data11 * tempTables[lengthIter].data00) - (tempTables[lengthIter].data01 * tempTables[lengthIter].data10) / math.sqrt(tempTables[lengthIter].data0X * tempTables[lengthIter].data1X * tempTables[lengthIter].dataX1 * tempTables[lengthIter].dataX0) else 0
            tempTables[lengthIter].IS = math.sqrt((tempTables[lengthIter].data11 * tempTables[lengthIter].data11) / abs((tempTables[lengthIter].dataX1 - tempTables[lengthIter].dataX0) * (tempTables[lengthIter].data1X - tempTables[lengthIter].data0X)))

            tempItem.clear()
            print("| ", tempTables[lengthIter].data11, " | ", tempTables[lengthIter].data10, " | ", tempTables[lengthIter].data1X, " |")
            print("| ", tempTables[lengthIter].data01, " | ", tempTables[lengthIter].data00, " | ", tempTables[lengthIter].data0X, " |")
            print("| ", tempTables[lengthIter].dataX1, " | ", tempTables[lengthIter].dataX0, " | ", tempTables[lengthIter].dataXX, " |")
            print("MEASURES supp:", tempTables[lengthIter].supp, " CC: ", tempTables[lengthIter].CC, " IS: ", tempTables[lengthIter].IS)  

            #print("TABLE data11: ", tempTables[lengthIter].data11, " data10: ", tempTables[lengthIter].data10, " data01: ", tempTables[lengthIter].data01, " data00: ", tempTables[lengthIter].data00)
            #print("TABLE data1X: ", tempTables[lengthIter].data1X, " dataX0: ", tempTables[lengthIter].dataX0, " dataX1: ", tempTables[lengthIter].dataX1, " data0X: ", tempTables[lengthIter].data0X, " dataXX: ", tempTables[lengthIter].dataXX)
            #print("MEASURES supp:", tempTables[lengthIter].supp, " CC: ", tempTables[lengthIter].CC, " IS: ", tempTables[lengthIter].IS)  
        

        if currentLargeItemSet == set([]):
            break

        #print("joinSet: ", currentLargeItemSet)
        candidateItemSet = getItemSetWithMinSup(currentLargeItemSet, transactionList, MINSUP, frequencyOfItemSets, lengthIter)
        #print("For length: ", lengthIter, " candidateOneItemSet: ", candidateOneItemSet)
        currentLargeItemSet = candidateItemSet
        lengthIter += 1

    finalLargeItemSet = []
    for key, value in largeItemSets.items():
        finalLargeItemSet.extend([(tuple(item), float(frequencyOfItemSets[item]) / len(transactionList)) for item in value])

    return finalLargeItemSet

def generateAssociationRules():
    associationRules = []
    for key, value in list(largeItemSets.items())[1:]:
        for item in value:
            subsets = map(frozenset, [x for x in getSubsets(item)])
            for element in subsets:
                remaining = item.difference(element)
                if len(remaining) > 0:
                    confidence = (float(frequencyOfItemSets[item]) / len(transactionList)) / (float(frequencyOfItemSets[remaining]) / len(transactionList))
                    if confidence > MINCONF:
                        associationRules.append(((tuple(element), tuple(remaining)), confidence))

    return associationRules

def printAll(finalLargeItemSets, associationRules):
    for item, support in sorted(finalLargeItemSets, key=lambda x: x[1]):
        print("item: %s , %.2f" % (str(item), support))

    for rule, confidence in sorted(associationRules, key=lambda x: x[1]):
        pre, post = rule
        print("Rule: %s => %s  %.2f" % (str(pre), str(post), confidence))

if __name__ == "__main__":
    rowRecords = readFromInputFile("SMALL-DATASET.csv")
    itemSet, transactionList = extractItemSetAndTransactionList(rowRecords)
    
    frequencyOfItemSets = defaultdict(int)

    # large itemset generation
    largeItemSets = dict()
    candidateOneItemSet = getItemSetWithMinSup(itemSet, transactionList, MINSUP, frequencyOfItemSets, 1)
    finalLargeItemSets = generateLargeItemSets(candidateOneItemSet)

    # association rules generation
    #associationRules = dict()
    #associationRules = generateAssociationRules()

    # print finalLargeItemSets and associationRules
    #printAll(finalLargeItemSets, associationRules)