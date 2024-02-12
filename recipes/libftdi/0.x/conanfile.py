import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir

required_conan_version = ">=1.53.0"


class LibFtdi(ConanFile):
    name = "libftdi"
    description = "libFTDI - FTDI USB driver with bitbang mode"
    license = "LGPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.intra2net.com/en/developer/libftdi"
    topics = ("libconfuse", "configuration", "parser")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_cpp_wrapper": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_cpp_wrapper": True,
    }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.enable_cpp_wrapper:
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libusb-compat/0.1.7", transitive_headers=True, transitive_libs=True)
        if self.options.enable_cpp_wrapper:
            self.requires("boost/1.83.0", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FTDIPP"] = self.options.enable_cpp_wrapper
        tc.variables["PYTHON_BINDINGS"] = False
        tc.variables["EXAMPLES"] = False
        tc.variables["DOCUMENTATION"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "CMAKE_BINARY_DIR", "PROJECT_BINARY_DIR")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "CMAKE_SOURCE_DIR", "PROJECT_SOURCE_DIR")
        replace_in_file(self, os.path.join(self.source_folder, "ftdipp", "CMakeLists.txt"),
                        "CMAKE_SOURCE_DIR", "PROJECT_SOURCE_DIR")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, "COPYING*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["ftdi"]
        self.cpp_info.requires = ["libusb-compat::libusb-compat"]
        if self.options.enable_cpp_wrapper:
            self.cpp_info.libs.append("ftdipp")
            self.cpp_info.requires.append("boost::headers")
