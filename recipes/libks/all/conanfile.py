import os
import sys

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, rmdir, copy
from conan.tools.build import check_max_cppstd
from conan.errors import ConanInvalidConfiguration


class LibksConan(ConanFile):
    name = "libks"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/signalwire/libks"
    license = "MIT"
    description = "Foundational support for signalwire C products"
    topics = ("libraries", "c")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]}
    default_options = {
        "shared": False,
        "fPIC": True
    }

    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # libks2/libks/ks_ssl.h:25:10: fatal error: openssl/ssl.h: No such file or directory
        self.requires("openssl/[>=1.1 <4]", transitive_headers=True)
        # libks2/libks/ks_types.h:163:18: fatal error: uuid/uuid.h: No such file or directory
        self.requires("util-linux-libuuid/2.39.2", transitive_headers=True)

    def validate(self):
        if self.settings.os == "Macos":
            check_max_cppstd(self, "17")
        elif self.settings.os == "Linux":
            raise ConanInvalidConfiguration("On Linux the recipe generate simbols that conflicts with the C++ standard library, contributions are welcome")
        elif self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Upstream does not install Windows files, cannot be used on Windows")

    def generate(self):
        deps = CMakeDeps(self)
        deps.set_property("util-linux-libuuid", "cmake_target_name", "LIBUUID::LIBUUID")
        deps.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["KS_STATIC"] = not self.options.shared
        tc.cache_variables["WITH_PACKAGING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "copyright", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "include", "libks2", "libks", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["ks2"]
        self.cpp_info.set_property("cmake_file_name", "LibKS2")
        self.cpp_info.set_property("cmake_target_name", "ks2")
        self.cpp_info.includedirs = ["include/libks2"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "rt", "atomic"]

        if not self.options.shared:
            self.cpp_info.defines.append("KS_DECLARE_STATIC=1")
        self.cpp_info.defines.append("HAVE_MALLOC=1")
        self.cpp_info.defines.append("HAVE_USLEEP=1")
        self.cpp_info.defines.append("HAVE_PTHREAD_ATTR_SETSCHEDPARAM=1")
        self.cpp_info.defines.append("HAVE_MEMMEM=1")
        self.cpp_info.defines.append("HAVE_STDLIB_H=1")
        self.cpp_info.defines.append("HAVE_SYS_TYPES_H=1")
        self.cpp_info.defines.append("HAVE_SYS_STAT_H=1")
        self.cpp_info.defines.append("HAVE_STRING_H=1")
        self.cpp_info.defines.append("HAVE_UNISTD_H=1")
        self.cpp_info.defines.append("HAVE_MEMORY_H=1")
        self.cpp_info.defines.append("HAVE_STRINGS_H=1")
        self.cpp_info.defines.append("HAVE_INTTYPES_H=1")
        self.cpp_info.defines.append("HAVE_STDINT_H=1")
        self.cpp_info.defines.append("HAVE_DLFCN_H=1")
        self.cpp_info.defines.append("HAVE_SCHED_H=1")
        self.cpp_info.defines.append("HAVE_DIRENT_H=1")
        self.cpp_info.defines.append("STDC_HEADERS=1")
        self.cpp_info.defines.append("TIME_WITH_SYS_TIME=1")
        self.cpp_info.defines.append("RETSIGTYPE=void")
        self.cpp_info.defines.append("HAVE_LIBCRYPTO=1")
        self.cpp_info.defines.append("HAVE_LIBSSL=1")
        self.cpp_info.defines.append("_REENTRANT=1")
        self.cpp_info.defines.append("__BYTE_ORDER=__LITTLE_ENDIAN")
