from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, save, load
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=1.53.0"


class FpngConan(ConanFile):
    name = "fpng"
    description = "Super fast C++ .PNG writer/reader"
    license = "unlicense",
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/richgel999/fpng"
    topics = ("png", "writer", "reader")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_sse": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_sse": False,
    }
    exports_sources = ["CMakeLists.txt"]

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FPNG_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["FPNG_WITH_SSE"] = self.options.with_sse
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        filename = os.path.join(self.source_folder, "src", "fpng.cpp")
        file_content = load(self, filename)
        license_start = "	This is free and unencumbered software"
        license_end = "*/"
        license_contents = file_content[file_content.find(license_start):file_content.find(license_end)]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["fpng"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m"]
