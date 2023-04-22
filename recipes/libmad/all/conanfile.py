from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class LibmadConan(ConanFile):
    name = "libmad"
    description = "MAD is a high-quality MPEG audio decoder."
    topics = ("mad", "MPEG", "audio", "decoder")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.underbit.com/products/mad/"
    license = "GPL-2.0-or-later"
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

    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBMAD_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["LIBMAD_VERSION"] = self.version
        tc.variables["LIBMAD_VERSION_MAJOR"] = Version(self.version).major
        tc.generate()

    def build(self):
        replace_in_file(
            self, os.path.join(self.source_folder, "msvc++", "mad.h"),
            "# define FPM_INTEL", "# define FPM_DEFAULT",
        )
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        for license_file in ("COPYRIGHT", "COPYING", "CREDITS"):
            copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["mad"]
