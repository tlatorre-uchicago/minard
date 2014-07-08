#include "curl/curl.h"
#include <string.h>

int main(){
  CURLcode res;
  static const char* message="name=L2&level=20&message=libcurltest&notify";
  
  CURL* curl = curl_easy_init();
  if(curl){
    curl_easy_setopt(curl, CURLOPT_URL, "http://snoplus:password@snopl.us/monitoring/log");
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, message);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, (long)strlen(message));
    res = curl_easy_perform(curl);
    if(res != CURLE_OK)
      fprintf(stderr, "Logging failed: %s\n", curl_easy_strerror(res));
    curl_easy_cleanup(curl);
  }
  else
    fprintf(stderr, "Could not initialize curl object");
  return 0;
}
