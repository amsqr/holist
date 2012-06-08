#include <iostream>
#include "dlqueue.hpp"
#include "download.hpp"

#ifndef __PROCESSOR_HPP
#define __PROCESSOR_HPP

class Processor {
	private:
		bool stopped;
	public:
		Processor();
		~Processor();
		void stop() { stopped = true; }
		void operator()();
};

#endif // __PROCESSOR_HPP
