# Algorithms
General usage from command line:
python fileName.py <dataset.csv> <MINSUP> <MINCONF> <startDominance>

## apriori-original.py
Generate all frequent itemsets based on MINSUP
Generate association rules based on MINCONF

## apriori-dominance.py
Generate <startDominance>-frequent itemsets and above based on MINSUP, then use dominance to prune this frequent itemset

## apriori-contingencyDominance.py
Construct a contingency table when generating <startDominance>-frequent itemsets and above based on MINSUP, then use dominance to prune this frequent itemset

# Datasets
## data1.csv
https://archive.ics.uci.edu/dataset/352/online+retail
After preprocessing has 1349 rows with (Avg: 18.8 items per transaction), 2337 unique items

## data2.csv
https://archive.ics.uci.edu/dataset/502/online+retail+ii
After preprocessing has 2138 rows with (Avg: 19.7 items per transaction), 3232 unique items

## data3.csv
https://www.kaggle.com/datasets/irfanasrullah/groceries
After preprocessing has 9835 rows with (Avg: 4.4 items per transaction), 331 unique items
