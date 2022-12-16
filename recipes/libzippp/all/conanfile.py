from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class LibZipppConan(ConanFile):
    name = "libzippp"
    description = "A simple basic C++ wrapper around the libzip library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ctabin/libzippp"
    topics = ("zip", "zlib", "libzip", "zip-archives", "zip-editing")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_encryption": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_encryption": False,
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

    def requirements(self):
        self.requires("zlib/1.2.13")
        if Version(self.version) == "4.0":
            self.requires("libzip/1.7.3")
        else:
            libzip_version = str(self.version).split("-")[1]
            self.requires("libzip/{}".format(libzip_version))

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        libzippp_version = str(self.version)
        if libzippp_version != "4.0" and len(libzippp_version.split("-")) != 2:
            raise ConanInvalidConfiguration("{}: version number must include '-'. (ex. '5.0-1.8.0')".format(self.name))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBZIPPP_INSTALL"] = True
        tc.variables["LIBZIPPP_INSTALL_HEADERS"] = True
        tc.variables["LIBZIPPP_ENABLE_ENCRYPTION"] = self.options.with_encryption
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_source(self):
        replace_in_file(self, os.path.join(self.source_folder, 'CMakeLists.txt'),
                        'find_package(LIBZIP MODULE REQUIRED)',
                        'find_package(libzip REQUIRED CONFIG)')

    def build(self):
        self._patch_source()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENCE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["zippp" if self.options.shared else "zippp_static"]

        self.cpp_info.names["cmake_find_package"] = "libzippp"
        self.cpp_info.names["cmake_find_package_multi"] = "libzippp"
        self.cpp_info.set_property("cmake_file_name", "libzippp")
        if self.options.with_encryption:
            self.cpp_info.defines.append("LIBZIPPP_WITH_ENCRYPTION")
