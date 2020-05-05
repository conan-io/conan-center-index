from conans import ConanFile, CMake, tools
import os


class EasyhttpcppConan(ConanFile):
    name = "easyhttpcpp"
    description = "A cross-platform HTTP client library with a focus on usability and speed"
    license = ("MIT",)
    topics = ("conan", "easyhttpcpp", "http", "client", "protocol")
    homepage = "https://github.com/sony/easyhttpcpp"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package_multi"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    requires = (
        "openssl/1.1.1g",
        "poco/1.10.1",
    )

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FORCE_SHAREDLIB"] = self.options.shared
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"].get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        libsuffix = ""
        if self.settings.os == "Windows":
            if not self.options.shared:
                libsuffix += "md"
        if self.settings.build_type == "Debug":
            libsuffix += "d"
        self.cpp_info.libs = ["easyhttp{}".format(libsuffix)]

