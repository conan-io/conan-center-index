from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class SrtConan(ConanFile):
    name = "srt"
    homepage = "https://github.com/Haivision/srt"
    description = "Secure Reliable Transport (SRT) is an open source transport technology that optimizes streaming performance across unpredictable networks, such as the Internet."
    topics = ("conan", "srt", "ip", "transport")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MPL-2.0"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    short_paths = True

    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
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

    @property
    def _has_posix_threads(self):
        return not (self.settings.os == "Windows" and (self.settings.compiler == "Visual Studio" or \
               (self.settings.compiler == "gcc" and self.settings.compiler.get_safe("threads") == "win32")))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("openssl/1.1.1q")
        if not self._has_posix_threads and not self._has_stdcxx_sync:
            self.requires("pthreads4w/3.0.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set (CMAKE_MODULE_PATH \"${CMAKE_CURRENT_SOURCE_DIR}/scripts\")",
                              "list(APPEND CMAKE_MODULE_PATH \"${CMAKE_CURRENT_SOURCE_DIR}/scripts\")")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_APPS"] = False
        self._cmake.definitions["ENABLE_LOGGING"] = False
        self._cmake.definitions["ENABLE_SHARED"] = self.options.shared
        self._cmake.definitions["ENABLE_STATIC"] = not self.options.shared
        if self._has_stdcxx_sync:
            self._cmake.definitions["ENABLE_STDCXX_SYNC"] = True
        self._cmake.definitions["ENABLE_ENCRYPTION"] = True
        self._cmake.definitions["USE_OPENSSL_PC"] = False
        if self.settings.compiler == "Visual Studio":
            # required to avoid warnings when srt shared, even if openssl shared,
            # otherwise upstream CMakeLists would add /DELAYLOAD:libeay32.dll to link flags
            self._cmake.definitions["OPENSSL_USE_STATIC_LIBS"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "srt"
        suffix = "_static" if self.settings.compiler == "Visual Studio" and not self.options.shared else ""
        self.cpp_info.libs = ["srt" + suffix]
        if self.options.shared:
            self.cpp_info.defines = ["SRT_DYNAMIC"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
