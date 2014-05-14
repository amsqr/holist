class DocumentIndexer(object):

    def queryId(self, docid):
        return self.index.query(docid)

    def queryText(self, textMinimalized, num_best):
        result = []
        plainTextSearchResults = self.textIndex.queryText(textMinimalized) # set of docIDs containing any words in the query
        textLSAVect = [val for (k,val) in self[textMinimalized]]

        for docId in  plainTextSearchResults:
            docLSAVect = self.corpus[docId].vectors[self.NAME]
            result.append((docId,self.compare(textLSAVect,docLSAVect))) #actual ranking determined by vecotr space similarity

        return sorted(result, key=lambda k: k[1], reverse=True)[:num_best]

    def compare(self, vec1, vec2, query=False):
        dot = numpy.dot(vec1, vec2)
        return dot / (abs(numpy.linalg.norm(vec1)) * abs(numpy.linalg.norm(vec2)))

    def indexDocuments(self, documents):
        ln.debug("now updating index.")
        documents = sorted(documents,key=lambda doc: doc.id)

        called = time.time()

        measured = 1.0
        averageComputeTime = 0.0

        relevancyMeasured = 1.0
        lenCorpus = float(self.corpus.fullLength())
        ln.debug("Full corpus size: %s", lenCorpus)
        averageRelevancyRate = 0.0

        numIndex = len(documents)

        averageRelevancyQueryTime = 0.0
        averageQueryTime = 0.0

        
        for idx, document in enumerate(documents):
            numOperations = (averageRelevancyRate * numIndex) * lenCorpus
            predictedTime = numOperations * averageComputeTime + numIndex * (averageQueryTime + averageRelevancyQueryTime)

            if idx % 100 == 0:
                sofar = time.time() - called
                ln.debug("idxd %s documents. avg: %.5fs/1kcomp, %.5fs/dbq, %.5fs relv qry, %.5f relv rate. Predicting %sm total, %sm left", 
                    idx, averageComputeTime * 1000, averageQueryTime, averageRelevancyQueryTime,averageRelevancyRate, int(predictedTime / 60), int((predictedTime - sofar) / 60))
            started = time.time()
            # iterate through all documents for indexing
            relevantDocIds = self.textIndex.queryText(document.preprocessed)
            relevantDocIds = sorted(relevantDocIds)
            relevantLen = len(relevantDocIds)
            
            
            relevantDocIds = [otherid for otherid in relevantDocIds if otherid < document.id] #filter out larger IDs, they're checked later
            comparisons = len(relevantDocIds)

            
            took = time.time() - started
            averageRelevancyQueryTime += (took - averageRelevancyQueryTime) / (idx + 1)

            started = time.time()
            #cache the docs in advance, in case we're connected to a db
            relevantDocsFull = self.corpus.getDocuments(relevantDocIds)
            

            took = time.time() - started
            averageQueryTime += (took - averageQueryTime) / (idx + 1)

            if comparisons: # relevancy is measured before actual comparisons are
                relevancyRate = relevantLen / lenCorpus
                averageRelevancyRate += float(relevancyRate - averageRelevancyRate) / measured

            started = time.time()
            for otherDoc in relevantDocsFull:
                #if otherDoc.id >= document.id:
                #    comparisons -= 1
                #    continue
                #otherDoc = self.corpus[otherDocId]
                #add to index
                comp = self.compare(document.vectors[self.NAME], otherDoc.vectors[self.NAME])

                self.index.addEntry(document.id, otherDoc.id, comp)
                self.index.addEntry(otherDoc.id, document.id, comp)

            took = time.time() - started

            if comparisons: # if anything was done, compute the averages to update the time prediction
                perdoc = took / comparisons
                averageComputeTime += (perdoc - averageComputeTime) / measured
                measured += 1