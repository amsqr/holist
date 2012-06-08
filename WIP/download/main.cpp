#include <iostream>
#include "processor.hpp"
#include "download.hpp"
using namespace std;

int main(int argc, char* argv[]) {
	DownloadTask dt("kernel.org");
	thread dthread(dt);

	Processor pr;
	thread pthread(pr);
	
	char buffer[100];
	cin.getline(buffer, 100);	
	
	pr.stop();

	return 0;
}

