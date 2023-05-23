#include <iostream>

#include "App.h"

int main()
{
  	uWS::App app;

  	app
  	.get("/", [](uWS::HttpResponse<false> *res, uWS::HttpRequest* req) {
  	  	res->end("Hello world!");
  	})
  	.listen(3000, [](auto* token) {
  	  	if (token) {
  	  	  	std::cout << "Serving over HTTP a 3000." << std::endl; 
  	  	}
  	});
}
