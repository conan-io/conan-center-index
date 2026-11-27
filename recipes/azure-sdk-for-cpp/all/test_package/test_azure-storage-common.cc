#include <azure/core/http/raw_response.hpp>
#include <azure/storage/common/storage_exception.hpp>

#include <memory>

using namespace Azure::Core::Http;
using namespace Azure::Storage;

int main()
{
  auto response = std::make_unique<RawResponse>(1, 1, HttpStatusCode::BadRequest, "Bad Request");
  auto exception = StorageException::CreateFromResponse(std::move(response));

  return exception.StatusCode == HttpStatusCode::BadRequest ? 0 : 1;
}
