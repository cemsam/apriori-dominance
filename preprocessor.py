import csv

transactionIdList = []
transactionListWithId = []
transactionListWithoutId = []
doneList = set()

file = open("transactionsTransformed.csv", "w")

with open('transactionsNew.csv', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    for row in reader:
        transactionIdList.append(row[0])
        transactionListWithId.append(row)
    #print(transactionIdList)
    
    for transactionId1 in transactionIdList:
        if (transactionId1 == "InvoiceNo"):
             continue
        for row in transactionListWithId:
            if (row[0] == "InvoiceNo"):
                continue
            if (transactionId1 == row[0] and (transactionId1 not in doneList)):
                file.write(row[2] + ',')
                print(row[0])
        doneList.add(transactionId1)
        file.write('\n')
        print(transactionId1)


file.close()
with open('transactionsTransformed.csv') as reader, open('transactionsTransformed.csv', 'r+') as writer:
  for line in reader:
    if line.strip():
      writer.write(line)
  writer.truncate()

print("done")