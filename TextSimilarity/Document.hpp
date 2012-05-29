//Class to represent a document, such as a news article

class Document
{
public:
	string getTitle();
	vector<string> *getText();
	Time createdWhen();
	URI source;
private:
	string title;
	vector<string> text;
	Time created;
	URI source;
}