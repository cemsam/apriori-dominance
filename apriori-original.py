import csv
from collections import defaultdict

MINSUP = 0.6

if __name__ == "__main__":
    # extract rows from csv file
    fileHandle = open("SMALL-DATASET.csv", "r")
    rowRecords = set()
    for row in fileHandle:
        row = row.strip().rstrip(",")
        rowRecords.add(row)
    print("rowRecords in csv file: ", rowRecords)

    # extract itemSet and transactionList
    transactionList = list()
    itemSet = set()

    for rowRecord in rowRecords:
        transactionList.append(rowRecord)
        for item in rowRecord.split(","):
            itemSet.add(item)

    print("itemset: ", itemSet)
    print("transactionList: ", transactionList)

    # calculate frequency of items in itemSet
    frequencyItemSet = defaultdict(int)

    for item in itemSet:
        for transaction in transactionList:
            if (item in transaction.split(",")) and not ("T" in item):
                frequencyItemSet[item] += 1

    print("frequencyItemset: ", frequencyItemSet)

    for item, count in frequencyItemSet.items():
        support = float(count) / len(transactionList)
        print("Item: ", item, " support: ", support)

    # if item's frequency is bigger than support add to new set
    frequentItemSet = set()
    for item, count in frequencyItemSet.items():
        support = float(count) / len(transactionList)
        if support >= MINSUP:
            frequentItemSet.add(item)

    print("frequent 1-itemSet: ", frequentItemSet)

    joinSet = set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == 2])

    print(joinSet)