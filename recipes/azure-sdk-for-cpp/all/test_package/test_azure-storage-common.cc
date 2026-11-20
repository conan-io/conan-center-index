#include <azure/core/http/raw_response.hpp>
#include <azure/storage/common/storage_exception.hpp>

#include <memory>
#include <string>
#include <vector>

using namespace Azure::Storage;

int main()
{
  // Parse an XML error body through the public API so that the XML backend
  // (webservices on Windows, libxml2 elsewhere) is linked and exercised.
  const std::string xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
                          "<Error><Code>Test</Code><Message>Test</Message></Error>";
  auto response = std::make_unique<Azure::Core::Http::RawResponse>(
      1, 1, Azure::Core::Http::HttpStatusCode::BadRequest, "Bad Request");
  response->SetHeader("Content-Type", "application/xml");
  response->SetBody(std::vector<uint8_t>(xml.begin(), xml.end()));
  StorageException exception = StorageException::CreateFromResponse(std::move(response));

  return exception.ErrorCode == "Test" ? 0 : 1;
}
