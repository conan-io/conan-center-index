#include <cstdlib>
#include "korgorusze/CLI.h"


namespace korg = korgorusze;

int main(void) {
    bool force;
    std::string_view path;
    auto argparse = korg::Command<"rm">{}
    .help("remove file")
    .add(
            korg::Flag<"force">{}
                    .longFlag<"force">()
                    .shortFlag<'f'>()
                    .set(force),
            korg::Argument<"path to file">{}
                    .set(path)
    );

    auto ret = argparse.parse("");

    return EXIT_SUCCESS;
}
