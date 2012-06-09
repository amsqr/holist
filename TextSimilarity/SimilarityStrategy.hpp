#include <Similarity.h>

template<typename Sim>
class SimilarityStrategy
{
private:
	Sim* typeVar;	//for specialization type verification
	DatabaseInterface databaseInterface;
public:
	vector< Similarity<Sim*> *> computeSimilarity(Sim* similable);
}