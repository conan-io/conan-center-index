from conan import ConanFile, tools
from conans import CMake
import os
import re
import functools

required_conan_version = ">=1.33.0"


class IMGUIConan(ConanFile):
    name = "imgui"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ocornut/imgui"
    description = "Bloat-free Immediate Mode Graphical User interface for C++ with minimal dependencies"
    topics = "gui", "graphical", "bloat-free"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def _patch_sources(self):
        # Ensure we take into account export_headers
        tools.files.replace_in_file(self, 
            os.path.join(self._source_subfolder, "imgui.h"),
            "#ifdef IMGUI_USER_CONFIG",
            "#include \"imgui_export_headers.h\"\n\n#ifdef IMGUI_USER_CONFIG"
        )

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        m = re.match(r'cci\.\d{8}\+(?P<version>\d+\.\d+)\.docking', str(self.version))
        version = tools.Version(m.group('version')) if m else tools.Version(self.version)
        backends_folder = os.path.join(
            self._source_subfolder,
            "backends" if version >= "1.80" else "examples"
        )
        self.copy(pattern="imgui_impl_*",
                  dst=os.path.join("res", "bindings"),
                  src=backends_folder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["imgui"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.srcdirs = [os.path.join("res", "bindings")]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
