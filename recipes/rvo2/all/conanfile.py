import os
from conan import ConanFile, tools
from conans import CMake


class Rvo2Conan(ConanFile):
    name = "rvo2"
    description = "Optimal Reciprocal Collision Avoidance"
    topics = ("conan", "collision", "avoidance", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/snape/RVO2"
    license = "Apache-2.0"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "RVO2-{}".format(self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"),
                    "add_subdirectory(examples)",
                    "")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                    "DESTINATION include",
                    "DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                    "RVO DESTINATION lib",
                    "RVO RUNTIME LIBRARY ARCHIVE")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
