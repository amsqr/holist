//This will be the abstract class to be inherited from by all similarity strategies. 

class SimilarityStrategy
{
public:
	virtual Similarity computeSimilarity(Document *doc1, Document *doc2);

};
