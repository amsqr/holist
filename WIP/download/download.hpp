#include <string>
#include <iostream>
#include <netdb.h>
#include <netinet/in.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include "dlqueue.hpp"

#ifndef __DOWNLOAD_TASK_HPP
#define __DOWNLOAD_TASK_HPP

class DownloadResult {
	private:
		char* buffer;
		int size;
	public:
		DownloadResult(char* buffer, int size) { this->buffer = buffer; this->size = size; }
		~DownloadResult() { delete buffer; }
		int getSize() { return size; }
		char* getBuffer() { return buffer; }
};

class DownloadTask {
	private:
		char* buffer;
		int buffer_size;
		int current_size;
		std::string path;
	public:
		DownloadTask(std::string path);
		~DownloadTask();
		void operator()();
		void append(char* buffer, int size);
		char* getBuffer(int* size);
};

#endif // __DOWNLOAD_TASK_HPP
