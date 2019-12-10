import os
from conans import ConanFile, CMake, tools


class TgbotConan(ConanFile):
    name = "tgbot"

    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://reo7sp.github.io/tgbot-cpp"
    description = "C++ library for Telegram bot API"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True, "shared": False}

    generators = "cmake", "cmake_find_package"
    exports_sources = ['CMakeLists.txt']
    requires = (
        "boost/1.71.0",
        "openssl/1.1.1d",
        "libcurl/7.66.0"
    )

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-cpp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        boost_version = self.deps_cpp_info['boost'].version
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "find_package(Boost 1.59.0 COMPONENTS system REQUIRED)",
                              "find_package(Boost {} COMPONENTS system REQUIRED)".format(boost_version))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_TESTS"] = False
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ['TgBot']
