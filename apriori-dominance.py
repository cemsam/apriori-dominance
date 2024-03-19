import time
import sys
#import pandas as pd
#from mlxtend.frequent_patterns import association_rules
from collections import defaultdict
from itertools import chain, combinations

class itemSetAndMeasures:
    itemset = 0
    measures = 0

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
        print("Frequent", lengthIter, "- itemSet: ", itemSet_list, ", support: ", round(frequencyOfItemSets[itemSet] / len(transactionList), 4))
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

def getConfidence(itemSet):
    itemSetSupport = 0
    remainingSupport = 0
    subsets = map(frozenset, [x for x in getSubsets(itemSet)])
    subsetSize = 0
    for element in subsets:
        subsetSize += 1
        remaining = itemSet.difference(element)
        if len(remaining) > 0:
            itemSetSupport += float(frequencyOfItemSets[itemSet]) / len(transactionList)
            remainingSupport += float(frequencyOfItemSets[remaining]) / len(transactionList)
    
    itemSetSupport = itemSetSupport / subsetSize
    remainingSupport = remainingSupport / subsetSize
    if remainingSupport == 0:
        return 0
        
    return round(itemSetSupport / remainingSupport, 4)

def getLift(itemSet, supportItemSet):
    elementSupport = 0
    remainingSupport = 0
    subsetSize = 0
    subsets = map(frozenset, [x for x in getSubsets(itemSet)])
    for element in subsets:
        subsetSize += 1
        remaining = itemSet.difference(element)
        if len(remaining) > 0:
            elementSupport += float(frequencyOfItemSets[element]) / len(transactionList)
            remainingSupport += float(frequencyOfItemSets[remaining]) / len(transactionList)

    elementSupport = elementSupport / subsetSize
    remainingSupport = remainingSupport / subsetSize
    if elementSupport * remainingSupport == 0:
        return 0
    return round(supportItemSet / (elementSupport * remainingSupport), 4)

def calculateMeasures(itemSetMeasures, k):
    support = round(float(frequencyOfItemSets[itemSetMeasures.itemset]) / len(transactionList), 4)
    confidence = getConfidence(itemSetMeasures.itemset)
    lift = getLift(itemSetMeasures.itemset, support)
    itemSetMeasures.measures = [support, confidence, lift]
    itemSet_list = list(itemSetMeasures.itemset)
    itemSet_list.sort()
    print(k, "-itemSet to pass to dominance: ", itemSet_list, itemSetMeasures.measures)


def generateLargeItemSets(candidateItemSet):
    currentLargeItemSet = candidateItemSet
    lengthIter = 2 # start from 2-itemsets
    while (currentLargeItemSet != set([])):
        largeItemSets[lengthIter - 1] = currentLargeItemSet
        newCandidateItemSet = joinSet(currentLargeItemSet, lengthIter)
        if newCandidateItemSet == set([]):
            print("============================== Cannot generate any", lengthIter, "- itemSets after union ==============================")
            break
        
        # start dominance depending on user input
        if (lengthIter >= k_ItemsetStartDominance) and (lengthIter > 3):
            currentLargeItemSet = getItemSetWithMinSup(newCandidateItemSet, transactionList, MINSUP, frequencyOfItemSets, lengthIter)
            if currentLargeItemSet == set([]):
                print("=========================== There are no", lengthIter, "- itemSets that satisfy MINSUP ===========================")
                break
            
            print("========================== Currently", len(currentLargeItemSet), "number of", lengthIter, "-itemSets satisfy MINSUP:", MINSUP, "==========================")
            finalItemSets = []
            print("==================== Calculating support, confidence, lift measures for", len(currentLargeItemSet), "number of", lengthIter, "-itemSets =====================")
            for itemSet in currentLargeItemSet:
                itemSetMeasures = itemSetAndMeasures()
                itemSetMeasures.itemset = itemSet
                calculateMeasures(itemSetMeasures, lengthIter)

                finalItemSets.append(itemSetMeasures)
            
            print("============================ Running Dominance with", len(finalItemSets), "number of", lengthIter, "-itemSets ======================================")
            undominatedItemsets = executeDominance(finalItemSets)
            currentLargeItemSet = set([])
            for itemSet in undominatedItemsets:
                itemSet_list = list(itemSet.itemset)
                itemSet_list.sort()
                print("Dominance result: ", itemSet_list, itemSet.measures)
                currentLargeItemSet.add(itemSet.itemset)
            print("================================================================================================")

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

def printAll(finalLargeItemSets, associationRules):
    #for item, support in sorted(finalLargeItemSets, key=lambda x: x[1]):
    #    print("item: %s , %.2f" % (str(item), support))

    confidenceSum = liftSum = 0
    for rule, confidence, lift in sorted(associationRules, key=lambda x: x[1]):
        pre, post = rule
        print("Rule: %s => %s " % (str(pre), str(post)), ", confidence: ", round(confidence, 4), ", lift: ", round(lift, 4))
        confidenceSum += confidence
        liftSum += lift
    print("============ Average confidence:", round(confidenceSum/len(associationRules),4), ", Average lift:", round(liftSum/len(associationRules),4),"=============")
    print("============================= Rule count", len(associationRules), "=============================")

if __name__ == "__main__":
    num_args = len(sys.argv)
    MINSUP = MINCONF = k_ItemsetStartDominance = 0
    if num_args != 5:
        print("Expected input format: python fileName.py <dataset.csv> <MINSUP> <MINCONF> <k_ItemsetStartDominance>")
        sys.exit()
    else:
        dataSetFile = "./datasets/" + sys.argv[1]
        MINSUP  = float(sys.argv[2])
        MINCONF = float(sys.argv[3])
        k_ItemsetStartDominance = int(sys.argv[4])
    
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
    print("============================= Total execution time:", round(endTime - startTime,2), "seconds =============================")