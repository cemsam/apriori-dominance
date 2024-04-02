# Algorithms
General usage from command line:
python fileName.py <dataset.csv> <MINSUP> <MINCONF> <startDominance>

## apriori-original.py
Generate all frequent itemsets based on MINSUP
Generate association rules based on MINCONF

## apriori-dominance.py
Generate 1, 2, 3-frequent itemsets based on MINSUP
Generate <startDominance>-frequent itemsets and above based on MINSUP, then use dominance to prune this frequent itemset

## apriori-contingencyDominance.py
Generate 1, 2, 3-frequent itemsets based on MINSUP
Construct a contingency table when generating <startDominance>-frequent itemsets and above based on MINSUP, then use dominance to prune this frequent itemset

# Datasets
## data1.csv
https://archive.ics.uci.edu/dataset/352/online+retail
https://www.kaggle.com/datasets/carrie1/ecommerce-data/data
Original name transactionsNew.csv
1349 rows with long transactions (Avg: 18.86 items per transaction), 2337 unique items

## data2.csv
https://www.kaggle.com/datasets/heeraldedhia/groceries-dataset
Original name groceries2.csv
3898 rows with medium length transactions (Avg: 10.94 items per transaction), 168 unique items

## data3.csv
https://www.kaggle.com/datasets/irfanasrullah/groceries
Original name groceries.csv
9835 rows with short transactions (Avg: 4.40 items per transaction), 331 unique items
