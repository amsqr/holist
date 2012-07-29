#include <Corellator.h>
class DocumentCorellator: public Corellator<Document>
{
private:
	// Sim* typeVar; //test variable for controlling specialization types
	DatabaseInterface databaseInterface;	//Singleton Interface to interact with MongoDB (and perhaps vocabulary index)
	vector<SimilarityStrategy<Document> *> knownStrategies;	
	SimilarityStrategy<Document>* preferredStrategy;
	
	~DocumentCorrelator();
	int receiveTask();
	int perform();
public:
	DocumentCorrelator();
	virtual vector<SimilarityStrategy<Document> *> getKnownStrategies() = 0;
	virtual SimilarityStrategy<Document>* getPreferredStrategy() = 0;

}