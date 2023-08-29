from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, load, save
from conan.tools.microsoft import msvc_runtime_flag, is_msvc
import os

required_conan_version = ">=1.54.0"

class TinycthreadConan(ConanFile):
    name = "tinycthread"
    description = "Small, portable implementation of the C11 threads API"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tinycthread/tinycthread"
    topics = ("thread", "c11", "portable")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    def configure(self):
        self.settings.compiler.rm_safe("libcxx")
        self.settings.compiler.rm_safe("cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TINYCTHREAD_DISABLE_TESTS"] = True
        tc.variables["TINYCTHREAD_INSTALL"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _extract_license(self):
        file = os.path.join(self.source_folder, "source", "tinycthread.h")
        file_content = load(self, file)

        license_start = file_content.find("Copyright")
        license_end = file_content.find("*/")
        license_contents = file_content[license_start:license_end]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self._extract_license()
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tinycthread"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
