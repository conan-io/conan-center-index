from conans import ConanFile, CMake, tools
import functools

required_conan_version = ">=1.33.0"


class GainputConan(ConanFile):
    name = "gainput"
    description = "Cross-platform C++ input library supporting gamepads, keyboard, mouse, touch."
    license = "MIT"
    topics = ("gainput", "input", "keyboard", "gamepad", "mouse", "multi-touch")
    homepage = "https://gainput.johanneskuhlmann.de"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["GAINPUT_SAMPLES"] = False
        cmake.definitions["GAINPUT_TESTS"] = False
        cmake.definitions["GAINPUT_BUILD_SHARED"] = self.options.shared
        cmake.definitions["GAINPUT_BUILD_STATIC"] = not self.options.shared
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        suffix = "{}{}".format("" if self.options.shared else "static",
                               "-d" if self.settings.build_type == "Debug" else "")
        self.cpp_info.libs = ["gainput" + suffix]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["xinput", "ws2_32"])
        elif self.settings.os == "Android":
            self.cpp_info.system_libs.extend(["native_app_glue", "log", "android"])
        elif tools.is_apple_os(self.settings.os):
            self.cpp_info.frameworks.extend(["Foundation", "IOKit", "GameController"])
            if self.settings.os == "iOS":
                self.cpp_info.frameworks.extend(["UIKit", "CoreMotion"])
            else:
                self.cpp_info.frameworks.append("AppKit")
