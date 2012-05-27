class TermCorrelator
{
public:
	TermCorrelator(URI databaseAddress);
	void setStrategy(int strategy);
	void setStrategy(Strategy *strategy);
	void setStrategy(string Strategy);
	int perform(Task *task);
private:
	URI databaseAddress;
	Strategy *currentStrategy;
}