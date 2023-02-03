#include <cstdlib>
#include <iostream>
#include <utility>
#include <folly/Format.h>
#include <folly/futures/Future.h>
#include <folly/executors/ThreadedExecutor.h>
#include <folly/Uri.h>
#include <folly/FBString.h>
#if FOLLY_HAVE_ELF
#include <folly/experimental/symbolizer/Elf.h>
#endif

static void print_uri(const folly::fbstring& value) {
    const folly::Uri uri(value);
    std::cout << "The authority from " << value << " is " << uri.authority() << std::endl;
}

int main() {
    folly::ThreadedExecutor executor;
    folly::Promise<std::string> promise;
    folly::Future<std::string> future = promise.getSemiFuture().via(&executor);
    folly::Future<folly::Unit> unit = std::move(future).thenValue(print_uri);
    promise.setValue("https://github.com/bincrafters");
    std::move(unit).get();
#if FOLLY_HAVE_ELF
    folly::symbolizer::ElfFile elffile;
#endif
    return EXIT_SUCCESS;
}
