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

def calculateMeasures(table):
    if table.data1X == 0:
        table.data1X = 1
    if table.data0X == 0:
        table.data0X = 1
    if table.dataX1 == 0:
        table.data1X = 1
    if table.dataX0 == 0:
        table.dataX0 = 1

    table.supp = round(table.data11 / table.dataXX, 3)
    table.CC = round(math.sqrt(table.data0X * table.data1X * table.dataX1 * table.dataX0) if (table.data11 * table.data00) - (table.data01 * table.data10) / math.sqrt(table.data0X * table.data1X * table.dataX1 * table.dataX0) else 0, 3)
    table.IS = round(math.sqrt((table.data11 * table.data11) / abs((table.dataX1 - table.dataX0) * (table.data1X - table.data0X))), 3)
    return table

def generateUniqueSubsetsTuple(frozen):
    # Convert from frozenlist to list
    itemSet = list(frozen)

    # Initialize an empty list to store subsets
    subsets = []

    # Iterate through all possible subset sizes
    for r in range(len(itemSet) + 1):
        # Generate all combinations of size r
        for subset in combinations(itemSet, r):
            # Create a tuple with the current subset and its complement
            currentTuple = (list(subset), [item for item in itemSet if item not in subset])
            subsets.append(currentTuple)

    # Return the first half of subsets to avoid duplicates
    uniqueSubsets = subsets[1:math.trunc(len(subsets) / 2)]

    return uniqueSubsets

def createBaseTable(table, subset):
    for transaction in transactionList:
        if (all(item in transaction for item in subset[0]) and (all(item in transaction for item in subset[1]))):
            table.data11 += 1
        elif (all(item in transaction for item in subset[0]) and not (all(item in transaction for item in subset[1]))):
            table.data10 += 1
        elif (not all(item in transaction for item in subset[0]) and (all(item in transaction for item in subset[1]))):
            table.data01 += 1
        elif (not all(item in transaction for item in subset[0]) and not (all(item in transaction for item in subset[1]))):
            table.data00 += 1

    table.data1X = table.data11 + table.data10
    table.dataX0 = table.data10 + table.data00
    table.dataX1 = table.data11 + table.data01
    table.data0X = table.data01 + table.data00
    table.dataXX = table.data1X + table.data0X
    
    return table

def generateLargeItemSets(candidateItemSet):
    currentLargeItemSet = candidateItemSet
    lengthIter = 2 # start from 2-itemsets
    while (currentLargeItemSet != set([])):
        largeItemSets[lengthIter - 1] = currentLargeItemSet
        currentLargeItemSet = joinSet(currentLargeItemSet, lengthIter)
        print("currentLargeItemSet: ", currentLargeItemSet)

        tempItem = []
        tempTables = {}
        for itemSet in currentLargeItemSet:
            print("itemSet: ", itemSet)
            uniqueSubsets = generateUniqueSubsetsTuple(itemSet)

            # loop over unique subsets of a large itemset
            tableCount = 0
            for uniqueSubset in uniqueSubsets:
                tempTables[lengthIter] = list()
                tempTables[lengthIter].append(tableCount)
                tempTables[lengthIter][tableCount] = contingencyTable()

                tempTables[lengthIter][tableCount] = createBaseTable(tempTables[lengthIter][tableCount], uniqueSubset)

                print("TABLE for uniqueSubset:", uniqueSubset)

                calculateMeasures(tempTables[lengthIter][tableCount])

                print("| ", tempTables[lengthIter][tableCount].data11, " | ", tempTables[lengthIter][tableCount].data10, " | ", tempTables[lengthIter][tableCount].data1X)
                print("| ", tempTables[lengthIter][tableCount].data01, " | ", tempTables[lengthIter][tableCount].data00, " | ", tempTables[lengthIter][tableCount].data0X)
                print("  ", tempTables[lengthIter][tableCount].dataX1, "   ", tempTables[lengthIter][tableCount].dataX0, "   ", tempTables[lengthIter][tableCount].dataXX)
                print("MEASURES supp:", tempTables[lengthIter][tableCount].supp, " CC: ", tempTables[lengthIter][tableCount].CC, " IS: ", tempTables[lengthIter][tableCount].IS)  

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