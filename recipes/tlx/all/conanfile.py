from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class TlxConan(ConanFile):
    name = "tlx"
    description = "tlx is a collection of C++ helpers and extensions " \
                  "universally needed, but not found in the STL."
    license = "BSL-1.0"
    topics = ("data-structure", "algorithm")
    homepage = "https://github.com/tlx/tlx"
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
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TLX_BUILD_TESTS"] = False
        tc.variables["TLX_USE_GCOV"] = False
        tc.variables["TLX_TRY_COMPILE_HEADERS"] = False
        tc.variables["TLX_MORE_TESTS"] = False
        tc.variables["TLX_BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["TLX_BUILD_SHARED_LIBS"] = self.options.shared
        # For msvc shared
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if Version(self.version) <= "0.6.1":
            # Relocatable shared libs on macOS
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Do not force PIC
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "-fPIC", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "CMake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tlx")
        self.cpp_info.set_property("cmake_target_name", "tlx")
        self.cpp_info.set_property("pkg_config_name", "tlx")
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
