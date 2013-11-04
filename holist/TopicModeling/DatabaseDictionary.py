#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module implements the concept of Dictionary -- a mapping between words and
their ids.

"""

from __future__ import with_statement

import logging
import itertools
from WordType import WordType
import smhasher
from holist.DatabaseInterface import DatabaseController as DB

logger = logging.getLogger('gensim.corpora.dictionary')

class DatabaseDictionary():
    """
    Dictionary encapsulates the mapping between normalized words and their integer ids.
    Each instance of this class will represent the same dictionary, provided the same 

    The main function is `doc2bow`, which converts a collection of words to its
    bag-of-words representation: a list of (word_id, word_frequency) 2-tuples.
    """
    def __init__(self, documents=None, createFromDatabase=False):
        
        self.token2id = {}
        self.id2token = {}

        self.size = 0
        #initialize the dictionary with what's already in the database

        if documents is not None:
            self.add_documents(documents)
        if createFromDatabase:
            for res in DB.tokens.find():
                self.size += 1
                self.id2token[res["_id"]] = res["token"]
                self.token2id[res["token"]] = res["_id"]

    def keys(self):
        return self.id2token.keys()

    def __getitem__(self, tokenid):
        return self.id2token[tokenid] # will throw for non-existent ids

    def getTokenID(self,token):
        return self.token2id[token]

    def __len__(self):
        """
        Return the number of token->id mappings in the dictionary.
        """
        return self.size

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

    def doc2bow(self, document, allow_update=False):
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
        document = sorted(document)
        # construct (word, frequency) mapping. in python3 this is done simply
        # using Counter(), but here i use itertools.groupby() for the job
        for token, group in itertools.groupby(document):
            if allow_update:
                if token not in self.id2token:
                    self.size += 1
                    #add type to dictionary
                    frequency = len(list(group)) # how many times does this word appear in the input document
                    wordType = WordType(token, None, frequency)
                    assignedId = DB.addWordType(wordType)

                    self.token2id[token] = assignedId
                    self.id2token[assignedId] = token

                    result[assignedId] = frequency
            #process tokens that are actually in the dictionary (if allow_update is set, then this is guaranteed)
            else:
                if token in self.token2id:
                    assignedId = self.token2id[token]
                    frequency = len(list(group)) # how many times does this word appear in the input document
                    result[assignedId] = frequency
            
        # return tokenids, in ascending id order
        result = sorted(result.iteritems())
        if return_missing:
            return result, missing
        else:
            return result

    