import time
import sys
from collections import defaultdict
from itertools import chain, combinations

def readFromInputFile(fileName):
    # extract rows from csv file
    fileHandle = open(fileName, "r")
    for row in fileHandle:
        row = row.strip().rstrip(",")
        rowRecords = frozenset(row.split(","))
        yield rowRecords

def getItemSetWithMinSup(itemSet, transactionList, MINSUP, frequencyOfItemSets, lengthIter):
    localCandidateItemSet = set()
    localSet = defaultdict(int)

    # calculate frequency of items in itemSet
    for item in itemSet:
        for transaction in transactionList:
            if item.issubset(transaction):
                frequencyOfItemSets[item] += 1
                localSet[item] += 1

    # if item's frequency is bigger than support add to new set
    for item, count in localSet.items():
        support = round(float(count) / len(transactionList), 4)
        if support >= MINSUP:
            localCandidateItemSet.add(item)

    for itemSet in localCandidateItemSet:
        itemSet_list = list(itemSet)
        itemSet_list.sort()
        print("Frequent", lengthIter, "- itemSet:", itemSet_list, ", support:", round(frequencyOfItemSets[itemSet] / len(transactionList), 4))
    print("============================= Frequent", lengthIter, "- itemSet count: ", len(localCandidateItemSet), "=============================")
    print(" ")

    return localCandidateItemSet

def joinSet(itemSet, itemSetLength):
        return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == itemSetLength])

'''
def joinSet(itemSet, length):
    """Join a set with itself and returns the n-element itemsets"""
    ret = []
    for i in itemSet:
        for j in itemSet:
            if len(i.union(j)) == length:
                ret.append(i.union(j))
    return set(ret)
'''

def getSubsets(arr):
    # Return non empty subsets
    return chain(*[combinations(arr, i + 1) for i, a in enumerate(arr)])

def extractItemSetAndTransactionList(rowRecords):
    transactionList = list()
    itemSet = set()
    
    for rowRecord in rowRecords:
        transaction = frozenset(rowRecord)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))

    return itemSet, transactionList

def generateLargeItemSets(candidateItemSet):
    currentLargeItemSet = candidateItemSet
    lengthIter = 2
    while (currentLargeItemSet != set([])):
        largeItemSets[lengthIter - 1] = currentLargeItemSet
        newCandidateItemSet = joinSet(currentLargeItemSet, lengthIter)
        if newCandidateItemSet == set([]):
            print("============================== Cannot generate any", lengthIter, "- itemSets after union ==============================")
            break

        currentLargeItemSet = getItemSetWithMinSup(newCandidateItemSet, transactionList, MINSUP, frequencyOfItemSets, lengthIter)
        if currentLargeItemSet == set([]):
            print("=========================== There are no", lengthIter, "- itemSets that satisfy MINSUP ===========================")
            break

        lengthIter += 1

    finalLargeItemSet = []
    for key, value in largeItemSets.items():
        finalLargeItemSet.extend([(tuple(item), float(frequencyOfItemSets[item]) / len(transactionList)) for item in value])

    return finalLargeItemSet

def generateAssociationRules():
    print("============================= Generating association rules =============================")
    associationRules = []
    for key, value in list(largeItemSets.items())[1:]:
        for item in value:
            item = list(item)
            item.sort()
            subsets = map(list, [x for x in getSubsets(item)])
            for element in subsets:
                #remaining = item.difference(element)
                remaining = list(item for item in item if item not in element)
                if len(remaining) > 0:
                    confidence = (float(frequencyOfItemSets[frozenset(item)]) / len(transactionList)) / (float(frequencyOfItemSets[frozenset(remaining)]) / len(transactionList))
                    lift = float(frequencyOfItemSets[frozenset(item)]) / len(transactionList) / ((float(frequencyOfItemSets[frozenset(element)]) / len(transactionList) * float(frequencyOfItemSets[frozenset(remaining)]) / len(transactionList)))
                    if confidence > MINCONF:
                        associationRules.append(((tuple(element), tuple(remaining)), confidence, lift))

    return associationRules

def printAll(associationRules):
    for rule, confidence, lift in sorted(associationRules, key=lambda x: x[1]):
        pre, post = rule
        print("Rule: %s => %s " % (str(pre), str(post)), ", confidence:", round(confidence, 4), ", lift:", round(lift, 4))
    print("============================= Rule count", len(associationRules), "=============================")

if __name__ == '__main__':
    num_args = len(sys.argv)
    MINSUP = MINCONF = 0
    if num_args != 4:
        print("Expected input format: python fileName.py <dataset.csv> <MINSUP> <MINCONF>")
        sys.exit()
    else:
        dataSetFile = "./datasets/" + sys.argv[1]
        MINSUP  = float(sys.argv[2])
        MINCONF = float(sys.argv[3])
    
    print("========================= Start execution for dataset:", sys.argv[1], "with MINSUP:", MINSUP, "and MINCONF", MINCONF, "=========================")
    startTime = time.time()
    rowRecords = readFromInputFile(dataSetFile)
    itemSet, transactionList = extractItemSetAndTransactionList(rowRecords)
    
    frequencyOfItemSets = defaultdict(int)

    # large itemset generation
    largeItemSets = dict()
    candidateOneItemSet = getItemSetWithMinSup(itemSet, transactionList, MINSUP, frequencyOfItemSets, 1)
    finalLargeItemSets = generateLargeItemSets(candidateOneItemSet)

    # association rules generation
    associationRules = dict()
    associationRules = generateAssociationRules()

    # print associationRules
    printAll(associationRules)
    
    endTime = time.time()
    print("======================== Total execution time:", round(endTime - startTime,2), "seconds ========================")