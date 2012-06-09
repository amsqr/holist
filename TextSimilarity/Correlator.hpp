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

	int receiveTask();
	int perform();
public:
	Correlator();
	vector<SimilarityStrategy<Sim*> *> getKnownStrategies();
	SimilarityStrategy<Sim*>* getPreferredStrategy();

}