#include <SimilarityStrategy.h>
#include <DatabaseInterface.h>

template<typename Sim>
class Correlator
{
private:
	Sim* typeVar; //test variable for controlling specialization types
	DatabaseInterface databaseInterface;	//Singleton Interface to interact with MongoDB (and perhaps vocabulary index)
	vector<SimilarityStrategy<Sim*> *> knownStrategies;	
	SimilarityStrategy<Sim*>* preferredStrategy;
	
	~Correlator();
	virtual int receiveTask() = 0;
	virtual int perform() = 0;
public:
	virtual vector<SimilarityStrategy<Sim*> *> getKnownStrategies() = 0;
	virtual SimilarityStrategy<Sim*>* getPreferredStrategy() = 0;

}