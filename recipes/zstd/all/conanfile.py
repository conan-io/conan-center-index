from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class ZstdConan(ConanFile):
    name = "zstd"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebook/zstd"
    description = "Zstandard - Fast real-time compression algorithm"
    topics = ("zstd", "compression", "algorithm", "decoder")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threading": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threading": True,
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
        tc.variables["ZSTD_BUILD_PROGRAMS"] = False
        tc.variables["ZSTD_BUILD_STATIC"] = not self.options.shared
        tc.variables["ZSTD_BUILD_SHARED"] = self.options.shared
        tc.variables["ZSTD_MULTITHREAD_SUPPORT"] = self.options.threading
        if Version(self.version) < "1.4.3":
            # Generate a relocatable shared lib on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Don't force PIC
        if Version(self.version) >= "1.4.5":
            replace_in_file(self, os.path.join(self.source_folder, "build", "cmake", "lib", "CMakeLists.txt"),
                                  "POSITION_INDEPENDENT_CODE On", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "build", "cmake"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        zstd_cmake = "libzstd_shared" if self.options.shared else "libzstd_static"
        self.cpp_info.set_property("cmake_file_name", "zstd")
        self.cpp_info.set_property("cmake_target_name", f"zstd::{zstd_cmake}")
        self.cpp_info.set_property("pkg_config_name", "libzstd")
        self.cpp_info.components["zstdlib"].set_property("pkg_config_name", "libzstd")
        self.cpp_info.components["zstdlib"].names["cmake_find_package"] = zstd_cmake
        self.cpp_info.components["zstdlib"].names["cmake_find_package_multi"] = zstd_cmake
        self.cpp_info.components["zstdlib"].set_property("cmake_target_name", f"zstd::{zstd_cmake}")
        self.cpp_info.components["zstdlib"].libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["zstdlib"].system_libs.append("pthread")
