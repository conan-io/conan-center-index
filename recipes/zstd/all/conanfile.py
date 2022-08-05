from conan import ConanFile
from conan.tools import files
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.scm import Version

import os

required_conan_version = ">=1.49.0"


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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            files.copy(self, patch["patch_file"], src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ZSTD_BUILD_PROGRAMS"] = False
        tc.variables["ZSTD_BUILD_STATIC"] = not self.options.shared
        tc.variables["ZSTD_BUILD_SHARED"] = self.options.shared
        tc.variables["ZSTD_MULTITHREAD_SUPPORT"] = self.options.threading

        if Version(self.version) < "1.4.3":
            # Generate a relocatable shared lib on Macos
            tc.variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

    def _patch_sources(self):
        files.apply_conandata_patches(self)

        # Don't force PIC
        if Version(self.version) >= "1.4.5":
            files.replace_in_file(self, os.path.join(self._source_subfolder, "build", "cmake", "lib", "CMakeLists.txt"),
                                  "POSITION_INDEPENDENT_CODE On", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        build_script_folder = os.path.join(self._source_subfolder, "build", "cmake")
        cmake.configure(build_script_folder=build_script_folder)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        
        license_folder = os.path.join(self.package_folder, "licenses")
        files.copy(self, pattern="LICENSE", src=self._source_subfolder, dst=license_folder)
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        zstd_cmake = "libzstd_shared" if self.options.shared else "libzstd_static"
        self.cpp_info.set_property("cmake_file_name", "zstd")
        self.cpp_info.set_property("cmake_target_name", "zstd::{}".format(zstd_cmake))
        self.cpp_info.set_property("pkg_config_name", "libzstd")
        self.cpp_info.components["zstdlib"].set_property("pkg_config_name", "libzstd")
        self.cpp_info.components["zstdlib"].names["cmake_find_package"] = zstd_cmake
        self.cpp_info.components["zstdlib"].names["cmake_find_package_multi"] = zstd_cmake
        self.cpp_info.components["zstdlib"].set_property("cmake_target_name", "zstd::{}".format(zstd_cmake))
        self.cpp_info.components["zstdlib"].libs = files.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["zstdlib"].system_libs.append("pthread")
