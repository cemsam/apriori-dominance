import csv
import time
#import pandas as pd
#from mlxtend.frequent_patterns  import association_rules
from collections import defaultdict
from itertools import chain, combinations


MINSUP = 0.01
MINCONF = 0.1

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

    # calculate frequency of items in itemSet
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
    lengthIter = 2
    while (currentLargeItemSet != set([])):
        largeItemSets[lengthIter - 1] = currentLargeItemSet
        newCandidateItemSet = joinSet(currentLargeItemSet, lengthIter)
        if newCandidateItemSet == set([]):
            print("============================== Cannot generate", lengthIter, "- itemSets ==============================")
            break

        #print("joinSet: ", newCandidateItemSet)
        currentLargeItemSet = getItemSetWithMinSup(newCandidateItemSet, transactionList, MINSUP, frequencyOfItemSets, lengthIter)
        for currentLargeItem in currentLargeItemSet:
            print("Frequent", lengthIter, "- itemSet: ", currentLargeItem)
        #print("For length: ", lengthIter, " candidateItemSet: ", candidateeItemSet)
        print("============================= Frequent", lengthIter, "- itemSet count: ", len(currentLargeItemSet), "=============================")
        print(" ")
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
    #for item, support in sorted(finalLargeItemSets, key=lambda x: x[1]):
    #    print("item: %s , %.2f" % (str(item), support))

    for rule, confidence in sorted(associationRules, key=lambda x: x[1]):
        pre, post = rule
        print("Rule: %s => %s  %.2f" % (str(pre), str(post), confidence))
    print("============================= Rule count", len(associationRules), "=============================")

if __name__ == "__main__":
    startTime = time.time()
    rowRecords = readFromInputFile("basket2.csv")
    itemSet, transactionList = extractItemSetAndTransactionList(rowRecords)
    
    frequencyOfItemSets = defaultdict(int)

    # large itemset generation
    largeItemSets = dict()
    candidateOneItemSet = getItemSetWithMinSup(itemSet, transactionList, MINSUP, frequencyOfItemSets, 1)
    finalLargeItemSets = generateLargeItemSets(candidateOneItemSet)

    # association rules generation
    associationRules = dict()
    associationRules = generateAssociationRules()

    # print finalLargeItemSets and associationRules
    printAll(finalLargeItemSets, associationRules)
    
    endTime = time.time()
    print("============================= Total execution time:", endTime - startTime, "seconds =============================")