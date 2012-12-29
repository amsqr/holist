#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module implements the concept of Dictionary -- a mapping between words and
their ids.

"""

from __future__ import with_statement

import logging
import itertools
from Token import Token
from ..DatabaseInterface import DatabaseController as DB


logger = logging.getLogger('gensim.corpora.dictionary')


class DatabaseDictionary():
    """
    Dictionary encapsulates the mapping between normalized words and their integer ids.
    Each instance of this class will represent the same dictionary, provided the same 

    The main function is `doc2bow`, which converts a collection of words to its
    bag-of-words representation: a list of (word_id, word_frequency) 2-tuples.
    """
    def __init__(self, documents=None):
        
        self.id2word = {}
        #initialize the dictionary with what's already in the database
        self.DBtokens = DB.tokens #MongoDB collections of tokens. {_id, token, frequency}
        if self.DBtokens == None:
            raise Exception("Dictionary couldn't open database collection")
        load()
        if documents is not None:
            self.add_documents(documents)

    def keys(self):
        return range(1,len(self)+1)

    def __getitem__(self, tokenid):
        return self.DBtokens.find({"_id": tokenid}) # will throw for non-existent ids

    def getTokenID(self,token):
        tokens = self.DBtokens.find({"token":token})
        if tokens.count() > 1:
            raise Exception("Multiple IDs for token "+token)
        elif tokens.count() < 1:
            raise Exception("No IDs found for token "+token)
        else:
            return tokens[0]["_id"]

    # def keys(self):
    #     """Return a list of all token ids."""
    #     return list(self.DBtokens.find())


    def __len__(self):
        """
        Return the number of token->id mappings in the dictionary.
        """
        
        return self.DBtokens.count()

    def __str__(self):
        return ("Dictionary(%i unique tokens)" % len(self))


    @staticmethod
    def from_documents(documents):
        return Dictionary(documents=documents)

    def add_documents(self, documents):
        """
        Build dictionary from a collection of documents. Each document is a list
        of tokens = **tokenized and normalized** utf-8 encoded strings.

        This is only a convenience wrapper for calling `doc2bow` on each document
        with `allow_update=True`.
        """
        for docno, document in enumerate(documents):
            if docno % 10000 == 0:
                logger.info("adding document #%i to %s" % (docno, self))
            _ = self.doc2bow(document, allow_update=True) # ignore the result, here we only care about updating token ids
#        logger.info("built %s from %i documents (total %i corpus positions)" %
 #                    (self, self.num_docs, self.num_pos))
    def load():
        for i,tokenObj in enumerate(self.DBtokens.find()):
            self.id2word[i] = tokenObj["token"])

    def save():
        for token in self.id2word:

    def doc2bow(self, document, allow_update=False, return_missing=False):
        """
        Convert `document` (a list of words) into the bag-of-words format = list
        of `(token_id, token_count)` 2-tuples. Each word is assumed to be a
        **tokenized and normalized** utf-8 encoded string. No further preprocessing
        is done on the words in `document`; apply tokenization, stemming etc. before
        calling this method.

        If `allow_update` is set, then also update dictionary in the process: create
        ids for new words. At the same time, update document frequencies -- for
        each word appearing in this document, increase its document frequency
        by one.

        If `allow_update` is **not** set, this function is `const`, aka read-only.
        """
        result = {} #in the form tokenid: frequency
        missing = {}
        document = sorted(document)
        # construct (word, frequency) mapping. in python3 this is done simply
        # using Counter(), but here i use itertools.groupby() for the job
        for word_norm, group in itertools.groupby(document):
            frequency = len(list(group)) # how many times does this word appear in the input document
            # self.token2id.get(word_norm, None)
            tokenid = hash(word_norm)
            # update how many times a token appeared in the document
            result[tokenid] = frequency

        if allow_update:
            # increase document count for each unique token that appeared in the document
            for tokenid in result.iterkeys():
                tokenObj = self.DBtokens.find_one({"_id":tokenid})
                # if foundTokens.count() > 1:
                #     raise Exception("found multiple tokens matching id "+str(tokenid))
                # tokenObj = foundTokens[0]
                updatedToken = Token(tokenid, tokenObj["token"], tokenObj["frequency"]+result[tokenid])
                DB.addToken(updatedToken)

        # return tokenids, in ascending id order
        result = sorted(result.iteritems())
        if return_missing:
            return result, missing
        else:
            return result