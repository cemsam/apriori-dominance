## apriori-original.py
Generate all frequent itemsets based on MINSUP
Generate association rules based on MINCONF

## apriori-dominance.py
Generate 1, 2, 3-frequent itemsets based on MINSUP
When generating 4-candidate itemsets and above, use dominance with support, confidence, lift measures

## apriori-newDominance.py
Generate 1, 2, 3-frequent itemsets based on MINSUP
Generate 4-frequent itemsets and above based on MINSUP, then use dominance to prune this frequent itemset
