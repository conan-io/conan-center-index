import os
import glob
from conans import ConanFile, tools, CMake


class VulkanLoaderConan(ConanFile):
    name = "vulkan-loader"
    description = "Vulkan Loader"
    topics = ("conan", "vulkan", "loader")
    homepage = "https://github.com/KhronosGroup/Vulkan-Loader"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "build_type", "compiler"
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        version = os.path.basename(url).replace(".tar.gz", "").replace(".zip", "")
        if version.startswith('v'):
            version = version[1:]
        extracted_dir = "Vulkan-Loader-" + version
        os.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        self.requires("vulkan-headers/{}".format(self.version))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os != "Windows":
            self.cpp_info.system_libs.extend(["dl", "pthread", "m"])
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.append("CoreFoundation")
        self.cpp_info.names["pkg_config"] = "Vulkan-Loader"
        self.cpp_info.names["cmake_find_package"] = "Vulkan-Loader"
        self.cpp_info.names["cmake_find_package_multi"] = "Vulkan-Loader"
