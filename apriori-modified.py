import csv
#import pandas as pd
#from mlxtend.frequent_patterns  import association_rules
from collections import defaultdict
from itertools import chain, combinations
import math

MINSUP = 0.008
MINCONF = 0.1

class contingencyTable:
    subset = 0
    data11 = 0
    data10 = 0
    data01 = 0
    data00 = 0
    data1X = 0
    dataX0 = 0
    dataX1 = 0
    data0X = 0
    dataXX = 0
    measures = 0
    supp = 0
    conf = 0
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
            #if not ("T" in item):
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
        table.dataX1 = 1
    if table.dataX0 == 0:
        table.dataX0 = 1

    table.supp = round(table.data11 / table.dataXX, 3)
    table.conf = round(table.data11 / table.data1X, 3)
    #table.CC = round(math.sqrt(table.data0X * table.data1X * table.dataX1 * table.dataX0) if (table.data11 * table.data00) - (table.data01 * table.data10) / math.sqrt(table.data0X * table.data1X * table.dataX1 * table.dataX0) else 0, 3)
    table.IS = round(math.sqrt((table.data11 * table.data11) / abs((table.dataX1 - table.dataX0) * (table.data1X - table.data0X))), 3)

    table.measures = [table.supp, table.conf, table.IS]
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

# Dominance algorithms
def getReferenceRule(s):
    candidateReferenceList = list(s[0].measures)
    for r in s:
        for i in range(len(r.measures)):
            candidateReferenceList[i] = max(r.measures[i], candidateReferenceList[i])
        
    return candidateReferenceList

def degSim(s,r2):
    return sum([abs(x-y) for x,y in zip(s, r2.measures)])/len(s)

def getrMinDegSim(s, reference):
    bestDegSim = degSim(reference, s[0])
    rStar = s[0]
    for r in s:
        auxDegSim = degSim(reference, r)
        if(auxDegSim < bestDegSim): #lower is better
            bestDegSim = auxDegSim
            rStar = r
    return rStar

#Dominates = True of all measures of self are greather or equal than measures in r2
def dominates(s, r2):
    for x,y in zip(r2.measures, s.measures):
        if (x>y): return False
    return True

#Strictly Dominates = Dominates and there is at least measure in self that is better than in r2
def strictlyDominates(s, r2):
    if(dominates(s, r2) and strictlyDominatesOneMeasure(s, r2)):
        return True
    return False

#Strictly in one measure
def strictlyDominatesOneMeasure(s, r2):
    for x,y in zip(s.measures, r2.measures):
        if (x>y): return True
    return False
    
def getUndominatedRules(s, referenceRule):
    selfC = s.copy() #Candidate undominated rules
    selfE = s.copy() #Current undominated rules
    sky = [] #Final undominated rules

    while(selfC): #While there are candidates
        rStar = getrMinDegSim(selfC, referenceRule) #r* <- r of C having min(DegSim(r,reference))
        selfC.remove(rStar) #C <- C\{r*}
        Sr = []
        sky.append(rStar)
    
        for e in selfE:
            if(strictlyDominates(rStar, e)):
                selfC.remove(e)
            elif(strictlyDominatesOneMeasure(e, rStar)):
                Sr.append(e)

        selfE = Sr #New current candidates are only undominated rules that dominates rStar in at least one measure

    return sky

def generateLargeItemSets(candidateItemSet):
    currentLargeItemSet = candidateItemSet
    lengthIter = 2 # start from 2-itemsets
    while (currentLargeItemSet != set([])):
        largeItemSets[lengthIter - 1] = currentLargeItemSet
        currentLargeItemSet = joinSet(currentLargeItemSet, lengthIter)
        print("currentLargeItemSet: ", currentLargeItemSet)
        if currentLargeItemSet == set([]):
            break
        
        # dont create tables for less and equal than 2-itemsets
        if lengthIter > 2:
            finalTables = [] # finalTables to store for each lengthIter and pass to Dominance
            tempTables = {} # tempTables as dict to hold list of tables for each uniqueSubset, lengthIter as key
            for itemSet in currentLargeItemSet:
                print("itemSet: ", itemSet)
                uniqueSubsets = generateUniqueSubsetsTuple(itemSet)

                # loop over unique subsets of a large itemset
                tableCount = 0
                tempTables[lengthIter] = list()
                for uniqueSubset in uniqueSubsets:
                    tempTables[lengthIter].append(tableCount)
                    tempTables[lengthIter][tableCount] = contingencyTable()

                    tempTables[lengthIter][tableCount] = createBaseTable(tempTables[lengthIter][tableCount], uniqueSubset)

                    print("TABLE for uniqueSubset:", uniqueSubset)

                    tempTables[lengthIter][tableCount].subset = uniqueSubset
                    calculateMeasures(tempTables[lengthIter][tableCount])

                    print("| ", tempTables[lengthIter][tableCount].data11, " | ", tempTables[lengthIter][tableCount].data10, " | ", tempTables[lengthIter][tableCount].data1X)
                    print("| ", tempTables[lengthIter][tableCount].data01, " | ", tempTables[lengthIter][tableCount].data00, " | ", tempTables[lengthIter][tableCount].data0X)
                    print("  ", tempTables[lengthIter][tableCount].dataX1, "   ", tempTables[lengthIter][tableCount].dataX0, "   ", tempTables[lengthIter][tableCount].dataXX)
                    print("MEASURES supp:", tempTables[lengthIter][tableCount].supp, " conf: ", tempTables[lengthIter][tableCount].conf, " IS: ", tempTables[lengthIter][tableCount].IS)
                    print(" ")

                    #measures = (tempTables[lengthIter][tableCount].supp, tempTables[lengthIter][tableCount].conf, tempTables[lengthIter][tableCount].IS)
                    #print("MEASURES : : ", measures)

                    tableCount += 1

                # create and assign finalTables for candidate k-itemsets
                maxConf = 0
                for uniqueTable in tempTables[lengthIter]:
                    if uniqueTable.conf > maxConf:
                        maxConf = uniqueTable.conf
                        finalTable = uniqueTable
                finalTables.append(finalTable)



            # ONLY FOR TEST HARD CODE RULES
            finalTables.clear()
            rule1 = contingencyTable()
            rule1.subset = 1
            rule1.measures = [0.20, 0.67, 0.02]
            finalTables.append(rule1)

            rule2 = contingencyTable()
            rule2.subset = 2
            rule2.measures = [0.10, 0.50, 0.00]
            finalTables.append(rule2)

            rule3 = contingencyTable()
            rule3.subset = 3
            rule3.measures = [0.10, 0.50, 0.02]
            finalTables.append(rule3)

            rule4 = contingencyTable()
            rule4.subset = 4
            rule4.measures = [0.20, 0.40, 0.10]
            finalTables.append(rule4)

            rule5 = contingencyTable()
            rule5.subset = 5
            rule5.measures = [0.20, 0.33, 0.02]
            finalTables.append(rule5)

            rule6 = contingencyTable()
            rule6.subset = 6
            rule6.measures = [0.20, 0.33, 0.10]
            finalTables.append(rule6)

            rule7 = contingencyTable()
            rule7.subset = 7
            rule7.measures = [0.10, 0.20, 0.01]
            finalTables.append(rule7)

            rule8 = contingencyTable()
            rule8.subset = 8
            rule8.measures = [0.10, 0.17, 0.02]
            finalTables.append(rule8)

            for table in finalTables:
                print("finalTables ", table.subset, table.measures)

            referenceRule = getReferenceRule(finalTables)
            print("referenceRule ", referenceRule)
                
            #degSim

            #getrMinDegSim
            rMinDegSim = getrMinDegSim(finalTables, referenceRule)
            print("rMinDegSim ", rMinDegSim)

            #strictlyDominatesOneMeasure
   
            #dominates

            #strictlyDominates

            #getUndominatedRules
            outp = getUndominatedRules(finalTables, referenceRule)
            for out in outp:
                print("OUTP ", out.subset, out.measures)
            
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