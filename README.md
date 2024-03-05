# Algorithms
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
Original name france_data.csv
392 rows with long transactions

## data2.csv
https://www.kaggle.com/datasets/heeraldedhia/groceries-dataset
Original name groceries2.csv
3898 rows with medium length transactions

## data3.csv
https://www.kaggle.com/datasets/irfanasrullah/groceries
Original name groceries.csv
9835 rows with short transactions