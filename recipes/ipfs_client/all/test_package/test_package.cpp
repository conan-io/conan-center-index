#include <boost/asio/io_context.hpp>
#include <ipfs_client/opinionated_context.h>

int main(void) {
    boost::asio::io_context io;
    auto ctxt = ipfs::start_default(io);
    auto mime = ctxt->MimeType("html", "a", "ipfs://bafyaafyscefakakvaaawceqgmexgq5dnnqmaccqcbaaq/a.html");
    mime.compare("text/html");
    return 0;
}
