#include <cstdlib>
#include <lsp/connection.h>
#include <lsp/io/socket.h>
#include <lsp/io/standardio.h>
#include <lsp/messagehandler.h>
#include <lsp/messages.h>

int main(void) {
    auto connection = lsp::Connection(lsp::io::standardIO());

    return EXIT_SUCCESS;
}
