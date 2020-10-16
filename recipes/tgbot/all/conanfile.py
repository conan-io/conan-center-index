import os
from conans import ConanFile, CMake, tools


class TgbotConan(ConanFile):
    name = "tgbot"

    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://reo7sp.github.io/tgbot-cpp"
    description = "C++ library for Telegram bot API"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True, "shared": False}

    generators = "cmake", "cmake_find_package"
    exports_sources = ['CMakeLists.txt', 'patches/*']
    requires = (
        "boost/1.71.0",
        "openssl/1.1.1d",
        "libcurl/7.67.0"
    )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-cpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_TESTS"] = False
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ['TgBot']
