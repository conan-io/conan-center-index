#include <google/cloud/speech/speech_client.h>
#include <iostream>

int main(int argc, char* argv[]) {
  if (argc != 1) {
    std::cerr << "Usage: speech\n";
    return 1;
  }
  std::cout << "Testing google-cloud-cpp::speech library " << google::cloud::version_string() << "\n";
  namespace speech = ::google::cloud::speech;
  auto client = speech::SpeechClient(speech::MakeSpeechConnection());
  return 0;
}
