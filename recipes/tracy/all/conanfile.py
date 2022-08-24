from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class TracyConan(ConanFile):
    name = "tracy"
    description = "C++ frame profiler"
    topics = ("profiler", "performance", "gamedev")
    homepage = "https://github.com/wolfpld/tracy"
    url = "https://github.com/conan-io/conan-center-index"
    license = ["BSD-3-Clause"]
    settings = "os", "compiler", "build_type", "arch"

    # Existing CMake tracy options with default value
    _tracy_options = {
        "enable": ([True, False], True),
        "callstack": ([True, False], False),
        "only_localhost": ([True, False], False),
        "no_broadcast": ([True, False], False),
        "no_code_transfer": ([True, False], False),
        "no_context_switch": ([True, False], False),
        "no_exit": ([True, False], False),
        "no_frame_image": ([True, False], False),
        "no_sampling": ([True, False], False),
        "no_verify": ([True, False], False),
        "no_vsync_capture": ([True, False], False),
    }
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        **{k: v[0] for k, v in _tracy_options.items()},
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        **{k: v[1] for k, v in _tracy_options.items()},
    }

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        # Set all tracy options in the correct form
        # For example, TRACY_NO_EXIT
        for opt in self._tracy_options.keys():
            switch = getattr(self.options, opt)
            opt = 'TRACY_' + opt.upper()
            self._cmake.definitions[opt] = switch

        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        self._cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["TracyClient"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")
