from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class CharlsConan(ConanFile):
    name = "charls"
    description = "C++ implementation of the JPEG-LS standard for lossless " \
                  "and near-lossless image compression and decompression."
    license = "BSD-3-Clause"
    topics = ("jpeg", "JPEG-LS", "compression", "decompression", )
    homepage = "https://github.com/team-charls/charls"
    url = "https://github.com/conan-io/conan-center-index"

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
            check_min_cppstd(self, 14)

        # brace initialization issue for gcc < 5
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("CharLS can't be compiled by {0} {1}".format(self.settings.compiler,
                                                                                         self.settings.compiler.version))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CHARLS_BUILD_FUZZ_TEST"] = False
        tc.cache_variables["CHARLS_BUILD_SAMPLES"] = False
        tc.cache_variables["CHARLS_BUILD_TESTS"] = False
        tc.cache_variables["CHARLS_INSTALL"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "charls")
        self.cpp_info.set_property("cmake_target_name", "charls")
        self.cpp_info.set_property("pkg_config_name", "charls")
        self.cpp_info.libs = collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append("CHARLS_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
