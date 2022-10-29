from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=1.46.0"


class TinyregexcConan(ConanFile):
    name = "tiny-regex-c"
    description = "Small and portable Regular Expression (regex) library written in C."
    license = "Unlicense"
    topics = ("tiny-regex-c", "regex")
    homepage = "https://github.com/kokke/tiny-regex-c"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "dot_matches_newline": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "dot_matches_newline": True,
    }

    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TINY_REGEX_C_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["RE_DOT_MATCHES_NEWLINE"] = self.options.dot_matches_newline
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tiny-regex-c"]
        self.cpp_info.defines = ["RE_DOT_MATCHES_NEWLINE={}".format("1" if self.options.dot_matches_newline else "0")]
