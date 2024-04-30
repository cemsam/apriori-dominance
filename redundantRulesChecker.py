import re
import sys

origname = sys.argv[1]
dominame = sys.argv[2]

origHandle = open(origname, "r")
domiHandle = open(dominame, "r")

rulesOrig = []
for row in origHandle:
    if "Rule: " in row:
        adj = row.split("Rule: ")[1].split(" =>")[0]
        cons = row.split(" => ")[1].split("  , c")[0]
        conf = row.split("confidence: ")[1].split(" , lift:")[0]
        lift = row.split(" , lift: ")[1].split("\n")[0]
        rulesOrig.append((adj, cons, float(conf), float(lift)))

rulesDomi = []
for row in domiHandle:
    if "Rule: " in row:
        adj = row.split("Rule: ")[1].split(" =>")[0]
        cons = row.split(" => ")[1].split("  , c")[0]
        conf = row.split("confidence: ")[1].split(" , lift:")[0]
        lift = row.split(" , lift: ")[1].split("\n")[0]
        rulesDomi.append((adj, cons, float(conf), float(lift)))

diffList = list(set(rulesOrig) - set(rulesDomi))
redundantRulesList = set()

print("There are", len(diffList), "number of difference in rules")
print("Searching for redundant rules")
for diffRule in diffList:
    for domiRule in rulesDomi:
        diffRuleAdj = re.findall("'([^']*)'", diffRule[0])
        domiRuleAdj = re.findall("'([^']*)'", domiRule[0])
        diffRuleCons = re.findall("'([^']*)'", diffRule[1])
        domiRuleCons = re.findall("'([^']*)'", domiRule[1])
        if (set(diffRuleAdj).issubset(set(domiRuleAdj)) and set(diffRuleCons).issubset(set(domiRuleCons))):
            print("Redundant rule:", diffRule[0], "=>", diffRule[1], "conf:", diffRule[2], "lift:", diffRule[3])
            redundantRulesList.add(diffRule)
            break

print("Redundant rule count", len(redundantRulesList))