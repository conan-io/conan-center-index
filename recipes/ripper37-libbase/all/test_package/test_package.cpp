#include <iostream>
#include <string>
#include <vector>

#include "base/callback.h"
#include "base/init.h"

#if defined(LIBBASE_MODULE_NET)
#include "base/net/init.h"
#include "base/net/simple_url_loader.h"
#include "base/net/resource_request.h"
#include "base/net/resource_response.h"
#endif  // defined(LIBBASE_MODULE_NET)

#if defined(LIBBASE_MODULE_WIN)
#include "base/message_loop/win/win_message_loop_attachment.h"
#endif  // defined(LIBBASE_MODULE_WIN)

#if defined(LIBBASE_MODULE_WX)
#include "base/message_loop/wx/wx_message_loop_attachment.h"
#endif // defined(LIBBASE_MODULE_WX)

int main(int argc, char* argv[]) {
  base::Initialize(argc, argv, {});
#if defined(LIBBASE_MODULE_NET)
  base::net::Initialize({});
#endif  // defined(LIBBASE_MODULE_NET)

  base::BindOnce([]() { std::cout << "Hello World!" << std::endl; }).Run();

  std::vector<std::string> enabled_components;
  enabled_components.push_back("core");
#if defined(LIBBASE_MODULE_NET)
  // Dummy code to check linkage
  if (argc < 0) {
    base::net::SimpleUrlLoader::DownloadUnbounded(
      base::net::ResourceRequest{"https://example.com"},
      base::BindOnce([](base::net::ResourceResponse) {}));
  }
  enabled_components.push_back("net");
#endif  // defined(LIBBASE_MODULE_NET)
#if defined(LIBBASE_MODULE_WIN)
  // Dummy code to check linkage
  if (argc < 0) {
    auto ml_attachment = base::win::WinMessageLoopAttachment::TryCreate();
  }
  enabled_components.push_back("win");
#endif  // defined(LIBBASE_MODULE_WIN)
#if defined(LIBBASE_MODULE_WX)
  // Dummy code to check linkage
  if (argc < 0) {
    auto ml_attachment = base::wx::WxMessageLoopAttachment{nullptr};
  }
  enabled_components.push_back("wx");
#endif  // defined(LIBBASE_MODULE_WX)

  std::cout << "Enabled components:";
  for (const auto& component : enabled_components) {
    std::cout << " " << component;
  }
  std::cout << std::endl;

#if defined(LIBBASE_MODULE_NET)
  base::net::Deinitialize();
#endif  // defined(LIBBASE_MODULE_NET)
  base::Deinitialize();
  return 0;
}
