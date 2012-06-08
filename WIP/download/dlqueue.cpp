#include "dlqueue.hpp"
using namespace std;

void DownloadQueue::enqueue(DownloadResult *element) {
	lock_guard<mutex> lock(m);
	queue.push(element);
	cond.notify_all();
}

DownloadResult* DownloadQueue::dequeue() {
	unique_lock<mutex> lock(m);
	while(queue.size() == 0) cond.wait(lock);
	
	DownloadResult* element = queue.front();
	queue.pop();
	return element;
}
