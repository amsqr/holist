#define CURL_STATICLIB

#include <stdio.h>
#include <curl/curl.h>
#include <curl/types.h>
#include <curl/easy.h>
#include <string>

size_t write_data(void *ptr, size_t size, size_t nmemb, FILE *stream)
{
	size_t written = fwrite(ptr, size, nmemb, stream);
	return written;
}

int main(int argc, char **argv)
{
	CURL *curl;
	FILE *fp;
	CURLcode res;
	char *url = "http://feeds.reuters.com/reuters/USpersonalfinanceNews?format=xml";
	char outfilename[FILENAME_MAX] = "outfile.txt";
	curl = curl_easy_init();
	if (curl){
		fp = fopen(outfilename, "wb");
		curl_easy_setopt(curl, CURLOPT_URL, url);
		curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_data);
		curl_easy_setopt(curl, CURLOPT_WRITEDATA, fp);
		res = curl_easy_perform(curl);
		curl_easy_cleanup(curl);
		fclose(fp);
	}
	return 0;
}
