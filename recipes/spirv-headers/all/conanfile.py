from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class SpirvheadersConan(ConanFile):
    name = "spirv-headers"
    homepage = "https://github.com/KhronosGroup/SPIRV-Headers"
    description = "Header files for the SPIRV instruction set."
    license = "MIT-KhronosGroup"
    topics = ("spirv", "spirv-v", "vulkan", "opengl", "opencl", "khronos")
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "compiler", "arch", "build_type"

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
              destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SPIRV_HEADERS_SKIP_EXAMPLES"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SPIRV-Headers")
        self.cpp_info.set_property("cmake_target_name", "SPIRV-Headers::SPIRV-Headers")
        self.cpp_info.set_property("pkg_config_name", "SPIRV-Headers")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "SPIRV-Headers"
        self.cpp_info.names["cmake_find_package_multi"] = "SPIRV-Headers"
        self.cpp_info.names["pkg_config"] = "SPIRV-Headers"
