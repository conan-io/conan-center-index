from conans import ConanFile, tools, CMake
import os
import glob


class LibKtxConan(ConanFile):
    name = "libktx"
    description = "Khronos Texture library and tool"
    license = "Apache-2.0"
    topics = ("conan", "ktx")
    homepage = "https://github.com/KhronosGroup/KTX-Software"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True
    }
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = "KTX-Software-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["KTX_FEATURE_STATIC_LIBRARY"] =
        not self.options.shared

        self._cmake.definitions["KTX_FEATURE_TESTS"] = False
        self._cmake.definitions["BUILD_TESTING"] = False

        self._cmake.configure(build_folder=self._build_subfolder,
                              source_folder=self._source_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSES/*", dst="", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        os.rename(os.path.join(self.package_folder, "LICENSES"),
                  os.path.join(self.package_folder, "license"))

    def package_info(self):
        self.cpp_info.libs = ["ktx"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "dl", "pthread"]
