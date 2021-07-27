from conans import ConanFile, tools, CMake
import os

required_conan_version = ">=1.33.0"


class WslayConan(ConanFile):
    name = "wslay"
    description = "The WebSocket library in C"
    topics = ("conan", "websockets", "rfc6455", "communication", "tcp")
    homepage = "https://tatsuhiro-t.github.io/wslay"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/*"]
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WSLAY_STATIC"] = not self.options.shared
        self._cmake.definitions["WSLAY_SHARED"] = self.options.shared
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libwslay"
        self.cpp_info.libs = ["wslay_shared" if self.options.shared else "wslay"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
