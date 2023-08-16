from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, save
import os

required_conan_version = ">=1.53.0"


class MinizipConan(ConanFile):
    name = "minizip"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://zlib.net"
    license = "Zlib"
    description = "An experimental package to read and write files in .zip format, written on top of zlib"
    topics = ("zip", "compression", "inflate")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "bzip2": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "bzip2": True,
        "tools": False,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
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

    def requirements(self):
        self.requires("zlib/1.2.13", transitive_headers=True)
        if self.options.bzip2:
            self.requires("bzip2/1.0.8", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MINIZIP_SRC_DIR"] = os.path.join(self.source_folder, "contrib", "minizip").replace("\\", "/")
        tc.variables["MINIZIP_ENABLE_BZIP2"] = self.options.bzip2
        tc.variables["MINIZIP_BUILD_TOOLS"] = self.options.tools
        # fopen64 and similar are unavailable before API level 24: https://github.com/madler/zlib/pull/436
        if self.settings.os == "Android" and int(str(self.settings.os.api_level)) < 24:
            tc.preprocessor_definitions["IOAPI_NO_64"] = "1"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def _extract_license(self):
        zlib_h = load(self, os.path.join(self.source_folder, "zlib.h"))
        return zlib_h[2:zlib_h.find("*/", 1)]

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["minizip"]
        self.cpp_info.includedirs.append(os.path.join("include", "minizip"))
        if self.options.bzip2:
            self.cpp_info.defines.append("HAVE_BZIP2")

        if self.options.tools:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
