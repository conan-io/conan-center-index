from conans import ConanFile, VisualStudioBuildEnvironment, CMake, tools

class CbindgenTestConan(ConanFile):
    name = "pact_mock_server_ffi_dll"
    version = "0.0.17"
    description = "Pact/Rust FFI bindings (DLL/Shared Lib)"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pact-foundation/pact-reference"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True
    requires = "openssl/1.1.1d"
    topics = ("pact", "consumer-driven-contracts", "contract-testing", "mock-server")

    def build(self):
        if self.settings.os == "Windows":
            url = ("https://github.com/pact-foundation/pact-reference/releases/download/libpact_mock_server_ffi-v%s/libpact_mock_server_ffi-windows-x86_64.dll.gz"
                   % (str(self.version)))
            tools.download(url, "pact_mock_server_ffi.dll.gz")
            tools.unzip("pact_mock_server_ffi.dll.gz")
            url = ("https://github.com/pact-foundation/pact-reference/releases/download/libpact_mock_server_ffi-v%s/libpact_mock_server_ffi-windows-x86_64.dll.lib.gz"
                   % (str(self.version)))
            tools.download(url, "pact_mock_server_ffi.dll.lib.gz")
            tools.unzip("pact_mock_server_ffi.dll.lib.gz")
        elif self.settings.os == "Linux":
            url = ("https://github.com/pact-foundation/pact-reference/releases/download/libpact_mock_server_ffi-v%s/libpact_mock_server_ffi-linux-x86_64.so.gz"
                % (str(self.version)))
            tools.download(url, "libpact_mock_server_ffi.so.gz")
            tools.unzip("libpact_mock_server_ffi.so.gz")
        elif self.settings.os == "Macos":
            url = ("https://github.com/pact-foundation/pact-reference/releases/download/libpact_mock_server_ffi-v%s/libpact_mock_server_ffi-osx-x86_64.dylib.gz"
                   % (str(self.version)))
            tools.download(url, "libpact_mock_server_ffi.dylib.gz")
            tools.unzip("libpact_mock_server_ffi.dylib.gz")
        else:
            raise Exception("Binary does not exist for these settings")
        tools.download(("https://github.com/pact-foundation/pact-reference/releases/download/libpact_mock_server_ffi-v%s/pact_mock_server_ffi.h"
                % (str(self.version))), "include/pact_mock_server_ffi.h")
        tools.download(("https://github.com/pact-foundation/pact-reference/releases/download/libpact_mock_server_ffi-v%s/pact_mock_server_ffi-c.h"
                % (str(self.version))), "include/pact_mock_server_ffi-c.h")

    def package(self):
        self.copy("libpact_mock_server_ffi*.so", "lib", "")
        self.copy("libpact_mock_server_ffi*.dylib", "lib", "")
        self.copy("pact_mock_server_ffi*.lib", "lib", "")
        self.copy("pact_mock_server_ffi*.dll", "bin", "")
        self.copy("*.h", "", "")

    def package_info(self):  # still very useful for package consumers
        self.cpp_info.libs = ["pact_mock_server_ffi"]
