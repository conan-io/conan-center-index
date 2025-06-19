
#include <curlpp/cURLpp.hpp>
#include <curlpp/Easy.hpp>
#include <curlpp/Options.hpp>

using namespace curlpp::options;

int main(int, char **) {
    curlpp::Easy myRequest;
	myRequest.setOpt<curlpp::options::Url>("http://example.com");
}
