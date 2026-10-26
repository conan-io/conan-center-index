#include <cassert>
#include <string>

#include "aistemsplitter/client.hpp"

int main() {
  auto input = aistemsplitter::SplitInput::direct_url("https://example.com/audio.mp3");
  assert(input.type == "direct_url");
  assert(input.url == "https://example.com/audio.mp3");

  aistemsplitter::Client client(
      "test-api-key", "https://api.example.test/v1",
      [](const aistemsplitter::HttpRequest& request) {
        assert(request.method == "GET");
        assert(request.url == "https://api.example.test/v1/credits");
        assert(request.headers.at("Authorization") == "Bearer test-api-key");
        return aistemsplitter::HttpResponse{
            200, {}, R"({"success":true,"data":{"balance":42,"unit":"credits"}})"};
      });

  auto credits = client.get_credits();
  assert(credits.balance == 42);
  assert(credits.unit == "credits");
}
