import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, replace_in_file, rm, rmdir, save
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class LibversionConan(ConanFile):
    name = "libversion"
    description = "Advanced version string comparison library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/repology/libversion"
    topics = ("versioning", "version")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_tools": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # Requires getopt.h and unistd.h
            del self.options.build_tools

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
        tc.generate()

    def _patch_sources(self):
        # Disable tests
        save(self, os.path.join(self.source_folder, "tests", "CMakeLists.txt"), "")
        # Disable tools
        if not self.options.get_safe("build_tools"):
            save(self, os.path.join(self.source_folder, "utils", "CMakeLists.txt"), "")
        # Install only the appropriate target
        target = "libversion" if self.options.shared else "libversion_static"
        replace_in_file(self, os.path.join(self.source_folder, "libversion", "CMakeLists.txt"),
                        "install(TARGETS libversion libversion_static EXPORT libversion)",
                        f"install(TARGETS {target} EXPORT libversion)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libversion")
        self.cpp_info.set_property("cmake_target_name", "libversion::libversion")
        self.cpp_info.set_property("pkg_config_name", "libversion")

        if is_msvc(self) and self.options.shared:
            self.cpp_info.libs = ["libversion"]
        else:
            self.cpp_info.libs = ["version"]

        if not self.options.shared:
            self.cpp_info.defines.append("LIBVERSION_STATIC_DEFINE")
