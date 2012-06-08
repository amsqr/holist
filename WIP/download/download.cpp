#include "download.hpp"
using namespace std;

DownloadTask::DownloadTask(string path) {
	this->path = path;
	buffer_size = 1024;
	buffer = new char[buffer_size];
	current_size = 0;
}

DownloadTask::~DownloadTask() {
	if (current_size > 0) {
		delete buffer;
	}	
}

char* DownloadTask::getBuffer(int *size) {
	char* rbuffer = new char[current_size+1];
	for(int i=0;i<current_size;i++) {
		rbuffer[i] = buffer[i];
	}
	*size = current_size+1;
	rbuffer[current_size] = '\0';
	return rbuffer;
}

void DownloadTask::append(char* new_data, int size) {
	if(current_size + size  > buffer_size) {
		int new_buffer_size = (current_size)*2;
		char* new_buffer = new char[new_buffer_size];
		for (int i=0;i<current_size;i++) {
			new_buffer[i] = buffer[i];
		}
		buffer = new_buffer;
		buffer_size = new_buffer_size;
	}
	for(int i=0;i<size;i++) {
		buffer[current_size+i] = new_data[i];
	}
	current_size += size;
}

void DownloadTask::operator()() {
	int status, sd;
        struct addrinfo hints;
        struct addrinfo *results;
        char* buffer = new char[1024];
        struct timeval tv;

        //initialize values
        memset(&tv, 0, sizeof(tv));
        memset(&hints, 0, sizeof(hints));
        tv.tv_sec = 1; //1sec timeout
        tv.tv_usec = 0;

        //set protocol information
        hints.ai_family = AF_UNSPEC;            //IPv4 or IPv6
        hints.ai_socktype = SOCK_STREAM;        //TCP
        hints.ai_flags = AI_PASSIVE;            //assign local interface address as source ip

        //rsolve domain name
        if ((status = getaddrinfo(path.c_str(),  "80", &hints, &results)) != 0) {
                fprintf(stderr, "URL: %s, getaddrinfo error: %s\n", path.c_str(), gai_strerror(status));
                return;
        }

        //ask os to create a socket
        if ((sd = socket(results->ai_family, results->ai_socktype, results->ai_protocol)) == -1) {
                fprintf(stderr, "URL: %s, socket error: %s\n", path.c_str(), strerror(errno));
                return;
        }

        //connect to remote address
        if (connect(sd, results->ai_addr, results->ai_addrlen) != 0) {
                fprintf(stderr, "URL: %s, connect error: %s\n", path.c_str(), strerror(errno));
                return;
        }

        //set timeout   
        if (setsockopt(sd, SOL_SOCKET, SO_RCVTIMEO, (char*)&tv, sizeof(struct timeval)) != 0) {
                fprintf(stderr, "URL: %s, couldn't set timeout: %s\n", path.c_str(), strerror(errno));
                return;
        }

	//send http get request
	string query = "GET / HTTP/1.1\n\n";
        //const char* msg = "GET / HTTP/1.1\nHost: kernel.org\n\n";
        if ( send(sd, /*msg*/query.c_str(), /*strlen(msg)*/query.length(), 0) == -1) {
                fprintf(stderr, "URL %s, sending failure:\n", path.c_str());
		return;
        }

        //receive content and write it to stdout
        int recvcount = 0;
        while( (recvcount = recv(sd, buffer, 10, 0)) != 0) {
                if (recvcount < 0) break; //timeout

		append(buffer, recvcount);
        }
        cout<<endl;

        //cleanup
        close(sd);
        freeaddrinfo(results);
	
	int size;
	DownloadQueue::getInstance().enqueue(new DownloadResult(getBuffer(&size), size));
}
