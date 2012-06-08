#include "processor.hpp"
#include "dlqueue.hpp"
using namespace std;

Processor::Processor() { }
Processor::~Processor() { }

void Processor::operator()() {
	while(!stopped) {
		DownloadResult* dt = DownloadQueue::getInstance().dequeue();
		int s = dt->getSize();
		char* data = dt->getBuffer();
		if (s > 0) {
			printf("%s", data);
		}
		delete data; //will also delete buffer
	}
}
