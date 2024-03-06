# Algorithms
General usage from command line:
python fileName.py <dataset.csv> <MINSUP> <MINCONF>

## apriori-original.py
Generate all frequent itemsets based on MINSUP
Generate association rules based on MINCONF

## apriori-dominance.py
Generate 1, 2, 3-frequent itemsets based on MINSUP
When generating 4-candidate itemsets and above, use dominance with support, confidence, lift measures

## apriori-newDominance.py
Generate 1, 2, 3-frequent itemsets based on MINSUP
Generate 4-frequent itemsets and above based on MINSUP, then use dominance to prune this frequent itemset

# Datasets
## data1.csv
https://www.kaggle.com/datasets/tanyadayanand/market-basket-analysis/data
Original name transactionsNew.csv
1349 rows with long transactions (Avg: 18.86 items per transaction)

## data2.csv
https://www.kaggle.com/datasets/heeraldedhia/groceries-dataset
Original name groceries2.csv
3898 rows with medium length transactions (Avg: 10.94 items per transaction)

## data3.csv
https://www.kaggle.com/datasets/irfanasrullah/groceries
Original name groceries.csv
9835 rows with short transactions (Avg: 4.40 items per transaction)