from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
from conan import tools as tools_legacy
import os

required_conan_version = ">=1.50.0"


class EdlibConan(ConanFile):
    name = "edlib"
    description = "Lightweight, super fast C/C++ (& Python) library for " \
                  "sequence alignment using edit (Levenshtein) distance."
    topics = ("edlib", "sequence-alignment", "edit-distance", "levehnstein-distance", "alignment-path")
    license = "MIT"
    homepage = "https://github.com/Martinsos/edlib"
    url = "https://github.com/conan-io/conan-center-index"

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
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def validate(self):
        if Version(self.version) < "1.2.7":
            if self.info.settings.compiler.cppstd:
                check_min_cppstd(self, 11)
            return

        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 14)

        minimum_version = self._minimum_compilers_version.get(str(self.info.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{}/{} requires C++14. Your compiler is unknown. Assuming it supports C++14.".format(self.name, self.version))
        elif Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("{}/{} requires C++14, which your compiler does not support.".format(self.name, self.version))

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["EDLIB_BUILD_EXAMPLES"] = False
        tc.variables["EDLIB_BUILD_UTILITIES"] = False
        if Version(self.version) >= "1.2.7":
            tc.variables["EDLIB_ENABLE_INSTALL"] = True
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0063"] = "NEW"
        # Needed because upstream CMakeLists overrides BUILD_SHARED_LIBS as a cache variable
        tc.cache_variables["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "edlib")
        self.cpp_info.set_property("cmake_target_name", "edlib::edlib")
        self.cpp_info.set_property("pkg_config_name", "edlib-{}".format(str(self.version).split(".")[0]))
        self.cpp_info.libs = ["edlib"]
        if self.options.shared:
            self.cpp_info.defines = ["EDLIB_SHARED"]
        if not self.options.shared:
            stdcpp_library = tools_legacy.stdcpp_library(self)
            if stdcpp_library:
                self.cpp_info.system_libs.append(stdcpp_library)
