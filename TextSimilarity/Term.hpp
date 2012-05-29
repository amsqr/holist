#include <string>
class Term
{
private:
	string term;
public:
	string get();
	int docFreq; //Document Frequency - Number of documents that are indexed by this term
	int colFreq; //Collection Frequency - Number of times this term appears in the collection
	int getIDF(int numDocs);
}