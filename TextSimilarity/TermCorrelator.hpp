class TermCorrelator
{
public:
	TermCorrelator(URI databaseAdress);
	void setStrategy(int strategy);
	void setStrategy(Strategy *strategy);
	void setStrategy(string Strategy);
	int perform(Task *task);
private:
	URI databaseAdress;
	Strategy *currentStrategy;
};