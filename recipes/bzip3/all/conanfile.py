from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get
import os

required_conan_version = ">=1.46.0"


class BZip3Conan(ConanFile):
    name = "bzip3"
    description = "A better and stronger spiritual successor to BZip2."
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kspalaiologos/bzip3"
    topics = ("bzip2", "lzma", "compression")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_thread": [True, False],
        "with_util": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_thread": True,
        "with_util": False,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # FIXME: could be supported on Windows:
        #  - MinGW with posix thread supports it out of the box
        #  - otherwise, add pthreads4w to requirements and link it in CMakeLists
        if self.settings.os == "Windows":
            del self.options.with_thread

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BZIP3_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["WITH_PTHREAD"] = self.options.get_safe("with_thread", False)
        tc.variables["WITH_UTIL"] = self.options.with_util
        tc.variables["VERSION"] = self.version
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "bzip3")
        self.cpp_info.libs = ["bzip3"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            if self.options.get_safe("with_thread", False):
                self.cpp_info.system_libs.append("pthread")
