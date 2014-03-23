from holist.core.dictionary.IDictionary import IDictionary
import itertools

class SimpleDictionary(IDictionary):
    def __init__(self, documents=None):
        self.token2id = dict()
        self.id2token = dict()
        self.size = 0

        if documents:
            self.addDocuments(documents)

    def keys(self):
        return self.id2token.keys()

    def __getitem__(self, tokenid):
        return self.id2token[tokenid]

    def getTokenID(self,token):
        return self.token2id[token]

    def __len__(self):
        return self.size
        
    def length(self):
        return len(self.token2id)

    def doc2bow(self, text, allow_update=False, return_missing=False):
        result = {} #in the form tokenid: frequency
        text = sorted(text)
        if return_missing:
            missing = []
        # construct (word, frequency) mapping. in python3 this is done simply
        # using Counter(), but here i use itertools.groupby() for the job
        for token, group in itertools.groupby(text):
            tokenid = self.token2id.get(token, None)
            if tokenid == None:
                if allow_update:
                    self.size += 1
                    #add type to dictionary
                    frequency = len(list(group)) # how many times does this word appear in the input document
                    # wordType = WordType(token, None, frequency)
                    assignedId = self.size
                    self.token2id[token] = assignedId
                    self.id2token[assignedId] = token
                    result[assignedId] = frequency

                if return_missing:
                    missing.append(token)
            #process tokens that are actually in the dictionary (if allow_update is set, then this is guaranteed)
            else:
                frequency = len(list(group)) # how many times does this word appear in the input document
                result[tokenid] = frequency
            
        # return tokenids, in ascending id order
        result = sorted(result.iteritems())
        if return_missing:
            return result, missing
        else:
            return result
