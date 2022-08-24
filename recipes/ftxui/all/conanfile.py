import os
import functools

from conan.tools.microsoft import is_msvc, msvc_runtime_flag
import conan.tools.files
from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class FTXUIConan(ConanFile):
    name = "ftxui"
    description = "C++ Functional Terminal User Interface."
    license = "MIT"
    topics = ("ncurses", "terminal", "screen", "tui")
    homepage = "https://github.com/ArthurSonzogni/FTXUI"
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

    def validate(self):
        compiler = self.settings.compiler
        version = tools.Version(self.settings.compiler.version)
        if compiler == 'gcc' and version < '8':
            raise ConanInvalidConfiguration("gcc 8 required")
        if compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        if is_msvc(self) and self.options.shared and "MT" in msvc_runtime_flag(self):
            raise ConanInvalidConfiguration("shared with static runtime not supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["FTXUI_BUILD_DOCS"] = False
        cmake.definitions["FTXUI_BUILD_EXAMPLES"] = False
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            conan.tools.files.patch(self, **patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ftxui")

        self.cpp_info.components["ftxui-dom"].set_property("cmake_target_name", "ftxui::dom")
        self.cpp_info.components["ftxui-dom"].libs = ["ftxui-dom"]
        self.cpp_info.components["ftxui-dom"].requires = ["ftxui-screen"]

        self.cpp_info.components["ftxui-screen"].set_property("cmake_target_name", "ftxui::screen")
        self.cpp_info.components["ftxui-screen"].libs = ["ftxui-screen"]

        self.cpp_info.components["ftxui-component"].set_property("cmake_target_name", "ftxui::component")
        self.cpp_info.components["ftxui-component"].libs = ["ftxui-component"]
        self.cpp_info.components["ftxui-component"].requires = ["ftxui-dom"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ftxui-component"].system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["ftxui-dom"].names["cmake_find_package"] = "dom"
        self.cpp_info.components["ftxui-dom"].names["cmake_find_package_multi"] = "dom"
        self.cpp_info.components["ftxui-screen"].names["cmake_find_package"] = "screen"
        self.cpp_info.components["ftxui-screen"].names["cmake_find_package_multi"] = "screen"
        self.cpp_info.components["ftxui-component"].names["cmake_find_package"] = "component"
        self.cpp_info.components["ftxui-component"].names["cmake_find_package_multi"] = "component"
