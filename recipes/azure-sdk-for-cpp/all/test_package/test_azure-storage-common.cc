#include <azure/storage/common/internal/xml_wrapper.hpp>
#include <azure/storage/common/storage_common.hpp>

using namespace Azure::Storage;

int main()
{
  ContentHash contentHash{};

  // Exercise the XML wrapper so that its platform-specific backend
  // (webservices on Windows, libxml2 elsewhere) is linked.
  _internal::XmlWriter writer;
  writer.Write(_internal::XmlNode{_internal::XmlNodeType::StartTag, "Test"});
  writer.Write(_internal::XmlNode{_internal::XmlNodeType::EndTag});
  writer.Write(_internal::XmlNode{_internal::XmlNodeType::End});

  return 0;
}
