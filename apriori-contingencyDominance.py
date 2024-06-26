import time
import math
import sys
#import pandas as pd
#from mlxtend.frequent_patterns  import association_rules
from collections import defaultdict
from itertools import chain, combinations

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
    jacc = 0
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
        support = round(float(count) / len(transactionList), 4)
        #print("Item: ", item, " support: ", support)
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
            itemSet.add(frozenset([item]))

    #print("itemset: ", itemSet)
    #print("transactionList: ", transactionList)
    return itemSet, transactionList

def calculateMeasures(table):
    table.supp = round(table.data11 / table.dataXX, 4)
    #table.conf = round(table.data11 / table.data1X, 4)
    table.jacc = round(table.data11 / (table.data1X + table.dataX1 - table.data1X), 4)
    table.IS = round(math.sqrt((table.data11 * table.data11) / abs((table.dataX1 - table.dataX0) * (table.data1X - table.data0X))), 4)

    table.measures = [table.supp, table.jacc, table.IS]
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

def executeDominance(finalTables):
    referenceRule = getReferenceRule(finalTables)
    undominatedRules = getUndominatedRules(finalTables, referenceRule)
    return undominatedRules

def generateLargeItemSets(candidateItemSet):
    currentLargeItemSet = candidateItemSet
    lengthIter = 2 # start from 2-itemsets
    while (currentLargeItemSet != set([])):
        largeItemSets[lengthIter - 1] = currentLargeItemSet
        newCandidateItemSet = joinSet(currentLargeItemSet, lengthIter)
        if newCandidateItemSet == set([]):
            print("============================== Cannot generate", lengthIter, "- itemSets ==============================")
            break
        
        # start dominance depending on user input
        if (lengthIter >= k_ItemsetStartDominance):
            currentLargeItemSet = getItemSetWithMinSup(newCandidateItemSet, transactionList, MINSUP, frequencyOfItemSets, lengthIter)
            if currentLargeItemSet == set([]):
                print("=========================== There are no", lengthIter, "- itemSets that satisfy MINSUP ===========================")
                break

            print("========================== Currently", len(currentLargeItemSet), "number of", lengthIter, "-itemSets satisfy MINSUP:", MINSUP, "==========================")
            finalTables = [] # finalTables to store for each lengthIter and pass to Dominance
            tempTables = {} # tempTables as dict to hold list of tables for each uniqueSubset, lengthIter as key
            print("==================== Creating contingency tables for", len(currentLargeItemSet), "number of CANDIDATE", lengthIter, "-itemSets =====================")
            for itemSet in currentLargeItemSet:
                print("Candidate", lengthIter, "itemSet: ", itemSet)
                uniqueSubsets = generateUniqueSubsetsTuple(itemSet)

                # loop over unique subsets of a large itemset
                tableCount = 0
                tempTables[lengthIter] = list()
                for uniqueSubset in uniqueSubsets:
                    tempTables[lengthIter].append(tableCount)
                    tempTables[lengthIter][tableCount] = contingencyTable()

                    tempTables[lengthIter][tableCount] = createBaseTable(tempTables[lengthIter][tableCount], uniqueSubset)

                    print("   TABLE for uniqueSubset:", uniqueSubset)

                    tempTables[lengthIter][tableCount].subset = uniqueSubset
                    calculateMeasures(tempTables[lengthIter][tableCount])

                    print("   | ", tempTables[lengthIter][tableCount].data11, " | ", tempTables[lengthIter][tableCount].data10, " | ", tempTables[lengthIter][tableCount].data1X)
                    print("   | ", tempTables[lengthIter][tableCount].data01, " | ", tempTables[lengthIter][tableCount].data00, " | ", tempTables[lengthIter][tableCount].data0X)
                    print("     ", tempTables[lengthIter][tableCount].dataX1, "   ", tempTables[lengthIter][tableCount].dataX0, "   ", tempTables[lengthIter][tableCount].dataXX)
                    print("   MEASURES supp:", tempTables[lengthIter][tableCount].supp, " jacc: ", tempTables[lengthIter][tableCount].jacc, " IS: ", tempTables[lengthIter][tableCount].IS)
                    print(" ")

                    tableCount += 1

                avgJacc = sumJacc = avgSupp = sumSupp = avgIS = sumIS = 0
                for uniqueTable in tempTables[lengthIter]:
                    sumJacc += uniqueTable.jacc
                    sumSupp += uniqueTable.supp
                    sumIS += uniqueTable.IS

                avgJacc = round(sumJacc/len(tempTables[lengthIter]),4)
                avgSupp = round(sumSupp/len(tempTables[lengthIter]),4)
                avgIS = round(sumIS/len(tempTables[lengthIter]),4)
                
                tempTables[lengthIter][0].jacc = avgJacc
                tempTables[lengthIter][0].supp = avgSupp
                tempTables[lengthIter][0].IS = avgIS
                tempTables[lengthIter][0].measures = [tempTables[lengthIter][0].supp, tempTables[lengthIter][0].jacc, tempTables[lengthIter][0].IS]
                    
                finalTables.append(tempTables[lengthIter][0])

            for table in finalTables:
                print("Final table to be passed to dominance: ", table.subset, table.measures)

            # DOMINANCE
            print("============================ Running Dominance with", len(finalTables), "number of", lengthIter, "-itemSets ======================================")
            undominatedItemsets = executeDominance(finalTables)

            currentLargeItemSet = set([])
            print("=======================================================================================")
            for itemSet in undominatedItemsets:
                # return to normal structure from subset structure
                itemSet.subset = [val for element in itemSet.subset for val in element]
                print("Dominance result: ", itemSet.subset, itemSet.measures)
                currentLargeItemSet.add(frozenset(itemSet.subset))
            print("=======================================================================================")

        else:
            currentLargeItemSet = getItemSetWithMinSup(newCandidateItemSet, transactionList, MINSUP, frequencyOfItemSets, lengthIter)
            
        #for currentLargeItem in currentLargeItemSet:
        #    print("Frequent", lengthIter, "- itemSet: ", currentLargeItem, ", support: ", round(frequencyOfItemSets[currentLargeItem] / len(transactionList), 4))
        #print("============================= Frequent", lengthIter, "- itemSet count: ", len(currentLargeItemSet), "=============================")
        #print(" ")
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
            subsets = map(frozenset, [x for x in getSubsets(item)])
            for element in subsets:
                #remaining = item.difference(element)
                remaining = list(item for item in item if item not in element)
                if len(remaining) > 0:
                    if float(frequencyOfItemSets[frozenset(remaining)]) > 0 and float(frequencyOfItemSets[frozenset(element)] > 0):
                        confidence = (float(frequencyOfItemSets[frozenset(item)]) / len(transactionList)) / (float(frequencyOfItemSets[frozenset(remaining)]) / len(transactionList))
                        lift = float(frequencyOfItemSets[frozenset(item)]) / len(transactionList) / ((float(frequencyOfItemSets[frozenset(element)]) / len(transactionList) * float(frequencyOfItemSets[frozenset(remaining)]) / len(transactionList)))
                        if confidence > MINCONF:
                            associationRules.append(((tuple(element), tuple(remaining)), confidence, lift))

    return associationRules

def printAll(finalLargeItemSets, associationRules):
    #for item, support in sorted(finalLargeItemSets, key=lambda x: x[1]):
    #    print("item: %s , %.2f" % (str(item), support))

    for rule, confidence, lift in sorted(associationRules, key=lambda x: x[1]):
        pre, post = rule
        print("Rule: %s => %s " % (str(pre), str(post)), ", confidence:", round(confidence, 4), ", lift:", round(lift, 4))
    print("============================= Rule count", len(associationRules), "=============================")

if __name__ == "__main__":
    num_args = len(sys.argv)
    MINSUP = MINCONF = k_ItemsetStartDominance = 0
    if num_args != 5 and num_args != 4:
        print("Expected input format: python fileName.py <dataset.csv> <MINSUP> <MINCONF> <k_ItemsetStartDominance>")
        sys.exit()
    else:
        dataSetFile = "./datasets/" + sys.argv[1]
        MINSUP  = float(sys.argv[2])
        MINCONF = float(sys.argv[3])
        if num_args == 5:
            k_ItemsetStartDominance = int(sys.argv[4])
        else:
            k_ItemsetStartDominance = 4
    
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

    # print finalLargeItemSets and associationRules
    printAll(finalLargeItemSets, associationRules)
    
    endTime = time.time()
    print("============================= Total execution time:", endTime - startTime, "seconds =============================")