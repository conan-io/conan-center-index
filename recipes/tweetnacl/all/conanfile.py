from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.32.0"


class TweetnaclConan(ConanFile):
    name = "tweetnacl"
    license = "Unlicense"
    homepage = "https://tweetnacl.cr.yp.to"
    url = "https://github.com/conan-io/conan-center-index"
    description = "TweetNaCl is the world's first auditable high-security cryptographic library"
    topics = ("nacl", "tweetnacl", "encryption", "signature", "hashing")
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    settings = "os", "compiler", "build_type", "arch"

    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os in ("Windows", "Macos"):
            if self.options.shared:
                raise ConanInvalidConfiguration("tweetnacl does not support shared on Windows and Madcos: it needs a randombytes implementation")

    def source(self):
        for url_sha in self.conan_data["sources"][self.version]:
            tools.files.download(self, url_sha["url"], os.path.basename(url_sha["url"]))
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
        self.copy("UNLICENSE", dst=os.path.join(self.package_folder, "licenses"))
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tweetnacl"]
