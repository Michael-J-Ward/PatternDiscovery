#ECLAT- Equivalence Class Transformation
#

from collections import defaultdict
import itertools

def getHorizontalData(filename):
    """Assumes first column in file is transaction ID followed by
    items in the transaction
    """
    with open(filename,'r') as f:
        data = {line.split()[0]: line.split()[1:] for line in f.readlines()}
    return data

def convertToVertical(data):
    """Assumes data is dictionary with transaction IDs as keys
    and a sequence of items as values.
    """
    vertical = defaultdict(set)
    for transaction in data:
        for item in data[transaction]:
            vertical[frozenset([item])].add(transaction)
    return vertical


def evalCandidates(candidates, itemLevel, frequent, lastLevel, minSupportCount):
    res = {}
    for setA, setB in candidates:
        candidate = setA.union(setB)

        if len(candidate) == itemLevel:          #check to see if the set has the right number of items
            valid = True
        else:
            continue                             #move to next candidate if not

        for subset in itertools.combinations(candidate, itemLevel-1):
            if frozenset(subset) not in lastLevel:          #make sure all subsets are frequent
                valid = False
                break

        tmp = frequent[setA] & frequent[setB]   #the transactions that contain both sets

        if valid and (len(tmp) > minSupportCount):
            res[candidate] = tmp
    return res

def findFrequentSets(data, minSup = 0.5):

    transactions = len(data)
    minSupportCount = minSup*transactions
    vData = convertToVertical(data)

    frequent = {k:v for k,v in vData.items() if len(v) > minSupportCount}
    lastLevel = {k for k in frequent.keys()}


    candidates = list(itertools.combinations(lastLevel,2))
    itemLevel = 2

    while candidates:
        tmp = evalCandidates(candidates, itemLevel, frequent, lastLevel, minSupportCount)
        lastLevel = {k for k in tmp.keys()}
        candidates = list(itertools.combinations(lastLevel,2))
        itemLevel += 1
        frequent.update(tmp)

    return frequent

def findRules(frequent, minConf = 0.5):
    """ This takes the output of findFrequentSets as input and
        outputs strong association rules
    """
    candidates = list(itertools.combinations(frequent.keys(),2))
    rules = []
    for setA, setB in candidates:
        transactionsA = frequent[setA]
        transactionsB = frequent[setB]
        if setA.issubset(setB):
            if float(len(transactionsB))/len(transactionsA) > minConf:
                rules.append(AssocRule(setA, transactionsA, setB, transactionsB))
        elif setB.issubset(setA):
            if float(len(transactionsA))/len(transactionsB) > minConf:
                rules.append(AssocRule(setB, transactionsB, setA, transactionsA))
        else:
            #neither set is a subset of the other, no potential rule
            continue
    return rules



class AssocRule(object):
    def __init__(self, setA, transactionsA, setB, transactionsB):
        self.setA = setA
        self.setB = setB
        self.transactions = {setA: transactionsA,
                             setB: transactionsB}
        self.support = len(transactionsB)   #absolute support
        self.confidence = float(self.support)/len(transactionsA)

    def __str__(self):
        return "{A} ---> {B} with absolute support of {S} and confidence {C}".format(A=self.setA, B= self.setB, S=self.support, C=self.confidence)