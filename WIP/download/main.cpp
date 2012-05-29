#include <iostream>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
using namespace std;

int main(int argc, char* argv[]) {
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
	hints.ai_family = AF_UNSPEC;		//IPv4 or IPv6
	hints.ai_socktype = SOCK_STREAM;	//TCP
	hints.ai_flags = AI_PASSIVE;		//assign local interface address as source ip

	//rsolve domain name
	if ((status = getaddrinfo("kernel.org",  "80", &hints, &results)) != 0) {
		fprintf(stderr, "getaddrinfo error: %s\n", gai_strerror(status));
		exit(1);
	}

	//ask os to create a socket
	if ((sd = socket(results->ai_family, results->ai_socktype, results->ai_protocol)) == -1) {
		fprintf(stderr, "socket error: %s\n", strerror(errno));
		exit(1);
	}

	//connect to remote address
	if (connect(sd, results->ai_addr, results->ai_addrlen) != 0) {
		fprintf(stderr, "connect error: %s\n", strerror(errno));
		exit(1);
	}
	
	//set timeout	
	if (setsockopt(sd, SOL_SOCKET, SO_RCVTIMEO, (char*)&tv, sizeof(struct timeval)) != 0) {
		fprintf(stderr, "couldn't set timeout: %s\n", strerror(errno));
		exit(1);
	}

	//send http get request
	const char* msg = "GET /index.shtml HTTP/1.1\nHost: kernel.org\n\n";
	if ( send(sd, msg, strlen(msg), 0) == -1) {
		fprintf(stderr, "sending failure:\n");
	}

	//receive content and write it to stdout
	int recvcount = 0;
	while( (recvcount = recv(sd, buffer, sizeof(buffer), 0)) != 0) {
		if (recvcount < 0) break; //timeout

		char* str = new char[recvcount+1];
		strncpy(str, buffer, recvcount+1);
		cout<<str;
		delete(str);
	}
	cout<<endl;

	//cleanup
	close(sd);
	freeaddrinfo(results);

	return 0;
}

