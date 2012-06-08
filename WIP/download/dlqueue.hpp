#include <queue>
#include <string>
#include <thread>
#include <condition_variable>

#ifndef __DOWNLOAD_QUEUE_HPP
#define __DOWNLOAD_QUEUE_HPP

class DownloadResult;

class DownloadQueue {
	private:
		std::queue<DownloadResult*> queue;
		std::condition_variable cond;
		std::mutex m;
	public:
		DownloadQueue() { };
		~DownloadQueue() { };
		static DownloadQueue& getInstance() {
			static DownloadQueue dq;
			return dq;
		}

		void enqueue(DownloadResult* element);
		DownloadResult* dequeue();
};

#endif // __DOWNLOAD_QUEUE_HPP
