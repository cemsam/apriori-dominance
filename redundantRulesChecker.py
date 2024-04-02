import re

fileHandle = open("./experiments-last2/data1/0.01/orig_data1.txt", "r")
rulesOrig = []
#print("ORIGINAL")
for row in fileHandle:
    if "Rule: " in row:
        adj = row.split("Rule: ")[1].split(" =>")[0]
        cons = row.split(" => ")[1].split("  , c")[0]
        conf = row.split("confidence: ")[1].split(" , lift:")[0]
        lift = row.split(" , lift: ")[1].split("\n")[0]
        #print(adj, cons, conf, lift)
        rulesOrig.append((adj, cons, float(conf), float(lift)))
print("Original rules parsed")

fileHandle = open("./experiments-last2/data1/0.01/domi_data1.txt", "r")
rulesDomi = []
#print("DOMINANCE")
for row in fileHandle:
    if "Rule: " in row:
        adj = row.split("Rule: ")[1].split(" =>")[0]
        cons = row.split(" => ")[1].split("  , c")[0]
        conf = row.split("confidence: ")[1].split(" , lift:")[0]
        lift = row.split(" , lift: ")[1].split("\n")[0]
        #print(adj, cons, conf, lift)
        rulesDomi.append((adj, cons, float(conf), float(lift)))
print("Dominance rules parsed")

diffList = list(set(rulesOrig) - set(rulesDomi))
redundantRulesList = set()
#print("Difference")
print("There are", len(diffList), "number of difference in rules")
print("Searching for redundant rules")
for diffRule in diffList:
    #print(diffRule)
    for domiRule in rulesDomi:
        diffRuleAdj = re.findall("'([^']*)'", diffRule[0])
        #print(diffRuleAdj)
        domiRuleAdj = re.findall("'([^']*)'", domiRule[0])
        #print(domiRuleAdj)
        diffRuleCons = re.findall("'([^']*)'", diffRule[1])
        #print(diffRuleCons)
        domiRuleCons = re.findall("'([^']*)'", domiRule[1])
        #print(domiRuleCons)
        if (set(diffRuleAdj).issubset(set(domiRuleAdj)) and set(diffRuleCons).issubset(set(domiRuleCons)) and (domiRule[2]>diffRule[2])):
            print("Redundant rule:", diffRule[0], "=>", diffRule[1], "conf:", diffRule[2], "lift:", diffRule[3])
            redundantRulesList.add(diffRule)
            break
print("Redundant rule count", len(redundantRulesList))