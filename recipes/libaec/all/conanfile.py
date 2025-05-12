from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rm, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class LibaecConan(ConanFile):
    name = "libaec"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.dkrz.de/k202009/libaec"
    description = "Adaptive Entropy Coding library"
    topics = "dsp", "encoding", "decoding"

    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        copy(self, "set_runtime_output_dir.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

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

    def validate(self):
        # libaec/1.0.6 uses "restrict" keyword which seems to be supported since Visual Studio 16.
        check_min_vs(self, 192)
        # libaec/1.0.6 fails to build aec_client command with debug and shared settings in Visual Studio.
        # Temporary, this recipe doesn't support these settings.
        if is_msvc(self) and self.options.shared and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration(f"{self.name} does not support debug and shared build in Visual Studio (currently)")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROJECT_libaec_INCLUDE"] = "set_runtime_output_dir.cmake"
        tc.cache_variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "set(CMAKE_C_STANDARD 99)", "set(CMAKE_C_STANDARD 11)")
        replace_in_file(self, cmakelists, "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")
        targets = "aec_shared sz_shared" if self.options.shared else "aec_static sz_static"
        aec_client = " aec_client" if Version(self.version) < "1.1" else ""
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                        f"install(TARGETS aec_static aec_shared sz_static sz_shared{aec_client})",
                        f"install(TARGETS {targets}{aec_client} ARCHIVE DESTINATION lib LIBRARY DESTINATION lib RUNTIME DESTINATION bin)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        copy(self, "libaec.h", os.path.join(self.build_folder, "include"), os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libaec")

        # CMake targets are based on
        # https://gitlab.dkrz.de/k202009/libaec/-/blob/master/cmake/libaec-config.cmake.in
        self.cpp_info.components["aec"].set_property("cmake_target_name", "libaec::aec")
        aec_name = "aec"
        if self.settings.os == "Windows" and not self.options.shared:
            aec_name = "aec-static"
        self.cpp_info.components["aec"].libs = [aec_name]

        self.cpp_info.components["sz"].set_property("cmake_target_name", "libaec::sz")
        szip_name = "sz"
        if self.settings.os == "Windows":
            szip_name = "szip" if self.options.shared else "szip-static"
        self.cpp_info.components["sz"].libs = [szip_name]

        # TODO: Legacy, to be removed on Conan 2.0
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
