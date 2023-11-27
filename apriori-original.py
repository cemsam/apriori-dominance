import csv
from collections import defaultdict

MINSUP = 0.2

def readFromInputFile(fileName):
    # extract rows from csv file
    fileHandle = open(fileName, "r")
    for row in fileHandle:
        row = row.strip().rstrip(",")
        rowRecords = frozenset(row.split(","))
        yield rowRecords
        print("rowRecords in csv file: ", rowRecords)

def getItemSetWithMinSup(itemSet, transactionList, MINSUP, frequentItemSet):
    localItemSet = set()
    itemSetFrequency = defaultdict(int)

    # calculate frequency of items in itemSet
    for item in itemSet:
        for transaction in transactionList:
            if item.issubset(transaction):
                frequentItemSet[item] += 1
                itemSetFrequency[item] += 1

    print("itemSetFrequency: ", itemSetFrequency)

    # if item's frequency is bigger than support add to new set
    for item, count in itemSetFrequency.items():
        support = float(count) / len(transactionList)
        print("Item: ", item, " support: ", support)
        if support >= MINSUP:
            localItemSet.add(item)

    print("frequent k-itemSet: ", localItemSet)
    return localItemSet

def joinSet(itemSet, itemSetLength):
        return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == itemSetLength])

if __name__ == "__main__":
    rowRecords = readFromInputFile("SMALL-DATASET.csv")
    # extract itemSet and transactionList
    transactionList = list()
    itemSet = set()

    for rowRecord in rowRecords:
        transaction = frozenset(rowRecord)
        transactionList.append(transaction)
        for item in transaction:
            if not ("T" in item):
                itemSet.add(frozenset([item]))

    print("itemset: ", itemSet)
    print("transactionList: ", transactionList)

    frequentItemSet = defaultdict(int)

    itemSetWithMinSup = getItemSetWithMinSup(itemSet, transactionList, MINSUP, frequentItemSet)

    currentSet = frequentItemSet
    lengthIter = 2
    while currentSet != set([]):
        currentSet = joinSet(currentSet, lengthIter)
        if currentSet == set([]):
            break
        
        print("joinSet: ", currentSet)
        itemSetWithMinSup = getItemSetWithMinSup(currentSet, transactionList, MINSUP, frequentItemSet)
        print("For length: ", lengthIter, " itemSetWithMinSup: ", itemSetWithMinSup)
        currentSet = itemSetWithMinSup
        lengthIter += 1