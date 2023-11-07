#include <stx/result.h>
#include <cstdio>
#include <string_view>
#include <iostream>

namespace fs {
    using stx::Ok, stx::Err;

    enum class Error {
        InvalidPath
    };

    template <typename T>
    using Result = stx::Result<T, Error>;

    // this is just a mock
    struct File {
        explicit File(std::string_view) noexcept {}
    };

    auto open(std::string_view path) noexcept -> Result<File> {
        if (path.empty())
            return Err(Error::InvalidPath);

        File file{path};

        return Ok(std::move(file));
    }
} // namespace fs

#ifdef STX_OVERRIDE_PANIC_HANDLER
void stx::panic_handler(std::string_view const& info,
                        stx::ReportPayload const& payload,
                        stx::SourceLocation const& source_location) noexcept {}
#endif
int main() {
    auto err = fs::open("").expect_err("should not be able to open file with empty filename");
    auto file = fs::open("example").expect("should be able to open file with name");
}
