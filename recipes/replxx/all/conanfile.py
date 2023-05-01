from conan import ConanFile
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class ReplxxConan(ConanFile):
    name = "replxx"
    description = """
    A readline and libedit replacement that supports UTF-8,
    syntax highlighting, hints and Windows and is BSD licensed.
    """
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AmokHuginnsson/replxx"
    topics = ("readline", "libedit", "UTF-8")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["REPLXX_BuildExamples"] = False
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.generate()

    def build(self):
        if Version(self.version) < "0.0.3":
            replace_in_file(self,
                os.path.join(self.source_folder, "src", "io.cxx"),
                "#include <array>\n",
                "#include <array>\n#include <stdexcept>\n"
            )
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["replxx"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]
        if not self.options.shared:
            self.cpp_info.defines.append("REPLXX_STATIC")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "replxx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "replxx"
