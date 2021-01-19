from conans import ConanFile, CMake, tools
import os


class SrtConan(ConanFile):
    name = "srt"
    homepage = "https://github.com/Haivision/srt"
    description = "Secure Reliable Transport (SRT) is an open source transport technology that optimizes streaming performance across unpredictable networks, such as the Internet."
    topics = ("conan", "srt", "ip", "transport")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MPL-2.0"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    short_paths = True

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _has_stdcxx_sync(self):
        return tools.Version(self.version) >= "1.4.2"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("openssl/1.1.1h")
        if self.settings.os == "Windows" and not self._has_stdcxx_sync:
            self.requires("pthreads4w/3.0.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_APPS"] = False
        self._cmake.definitions["ENABLE_LOGGING"] = False
        self._cmake.definitions["ENABLE_SHARED"] = self.options.shared
        self._cmake.definitions["ENABLE_STATIC"] = not self.options.shared
        self._cmake.definitions["ENABLE_STDCXX_SYNC"] = self._has_stdcxx_sync
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        tools.patch(**self.conan_data["patches"][self.version])
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
