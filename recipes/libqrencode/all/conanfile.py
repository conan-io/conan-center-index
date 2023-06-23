from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.54.0"


class LibqrencodeConan(ConanFile):
    name = "libqrencode"
    description = "A fast and compact QR Code encoding library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fukuchi/libqrencode"
    license = "LGPL-2.1-or-later"
    topics = ("qr-code", "encoding")

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

    def export_sources(self):
        export_conandata_patches(self)

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
        tc.variables["WITH_TOOLS"] = False
        tc.variables["WITH_TESTS"] = False
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # libpng is required by tools only & libiconv is not used at all
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "find_package(PNG)", "")
        replace_in_file(self, cmakelists, "find_package(Iconv)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libqrencode")
        suffix = "d" if is_msvc(self) and self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"qrencode{suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
