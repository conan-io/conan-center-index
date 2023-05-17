from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class TmxliteConan(ConanFile):
    name = "tmxlite"
    description = "A lightweight C++14 parsing library for tmx map files created with the Tiled map editor."
    license = "Zlib"
    topics = ("tmxlite", "tmx", "tiled-map", "parser")
    homepage = "https://github.com/fallahn/tmxlite"
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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("miniz/2.2.0")
        self.requires("pugixml/1.12.1")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)
        if self.info.settings.compiler == "gcc" and Version(self.info.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration("gcc < 5 not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TMXLITE_STATIC_LIB"] = not self.options.shared
        tc.variables["PROJECT_STATIC_RUNTIME"] = False
        tc.variables["USE_RTTI"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # unvendor miniz
        rm(self, "miniz*", os.path.join(self.source_folder, "tmxlite", "src"))
        replace_in_file(self, os.path.join(self.source_folder, "tmxlite", "src", "CMakeLists.txt"),
                              "${PROJECT_DIR}/miniz.c", "")
        # unvendor pugixml
        rmdir(self, os.path.join(self.source_folder, "tmxlite", "src", "detail"))
        replace_in_file(self, os.path.join(self.source_folder, "tmxlite", "src", "CMakeLists.txt"),
                              "${PROJECT_DIR}/detail/pugixml.cpp", "")
        # Don't inject -O3 in compile flags
        replace_in_file(self, os.path.join(self.source_folder, "tmxlite", "CMakeLists.txt"),
                              "-O3", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "tmxlite"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append("TMXLITE_STATIC")
        if self.settings.os == "Android":
            self.cpp_info.system_libs.append("log", "android")
