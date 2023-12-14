from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
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

    def export_sources(self):
        export_conandata_patches(self)

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
        tc.variables["REPLXX_BUILD_EXAMPLES"] = False
        tc.variables["REPLXX_BUILD_PACKAGE"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "replxx")
        self.cpp_info.set_property("cmake_target_name", "replxx::replxx")
        libname = "replxx"
        if is_msvc(self) and not self.options.shared:
            libname += "-static"
        if self.settings.build_type == "Debug":
            libname += "-d"
        elif self.settings.build_type == "RelWithDebInfo":
            libname += "-rd"
        self.cpp_info.libs = [libname]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]
        if not self.options.shared:
            self.cpp_info.defines.append("REPLXX_STATIC")
