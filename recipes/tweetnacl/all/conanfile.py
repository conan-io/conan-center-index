from conans import ConanFile, CMake, tools
import os


TWEETNACL_LICENSE = """
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this software, either in source code form or as a compiled binary, for any purpose, commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this software dedicate any and all copyright interest in the software to the public domain. We make this dedication for the benefit of the public at large and to the detriment of our heirs and successors. We intend this dedication to be an overt act of relinquishment in perpetuity of all present and future rights to this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to http://unlicense.org/
"""


class TweetnaclConan(ConanFile):
    name = "tweetnacl"
    license = "Public Domain"
    homepage = "https://tweetnacl.cr.yp.to"
    url = "https://github.com/conan-io/conan-center-index"
    description = "TweetNaCl is the world's first auditable high-security cryptographic library"
    exports = ["PUBLIC_DOMAIN_LICENSE.md", "LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    settings = "os", "compiler", "build_type", "arch"

    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        for url_sha in self.conan_data["sources"][self.version]:
            tools.download(url_sha["url"], os.path.basename(url_sha["url"]))
            tools.check_sha256(os.path.basename(url_sha["url"]), url_sha["sha256"])

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.save(os.path.join(self.package_folder, "licenses", "COPYING"),
                   TWEETNACL_LICENSE)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
