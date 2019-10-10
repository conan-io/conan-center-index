from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class AmqpcppConan(ConanFile):
    name = "amqp-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CopernicaMarketingSoftware/AMQP-CPP"
    topics = ("amqp", "network", "queue", "conan")
    license = "Apache-2.0"
    description = "C++ library for asynchronous non-blocking communication with RabbitMQ"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, 'fPIC': True}
    generators = "cmake"

    exports_sources = ["CMakeLists.txt"]

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("AMQP-CPP-" + self.version, self._source_subfolder)
        os.rename(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                  os.path.join(self._source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self._source_subfolder, "CMakeLists.txt"))

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported by upstream")

    def requirements(self):
        self.requires.add("openssl/1.0.2t")

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions['AMQP-CPP_BUILD_SHARED'] = self.options.shared
        cmake.definitions['AMQP-CPP_BUILD_EXAMPLES'] = False
        cmake.definitions['AMQP-CPP_LINUX_TCP'] = True

        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = CMake(self)
        cmake = self._configure_cmake()
        cmake.install()

    def package(self):
        cmake = CMake(self)
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread"])
