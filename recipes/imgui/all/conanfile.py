import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, replace_in_file

required_conan_version = ">=1.53.0"


class IMGUIConan(ConanFile):
    name = "imgui"
    description = "Bloat-free Immediate Mode Graphical User interface for C++ with minimal dependencies"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ocornut/imgui"
    topics = ("gui", "graphical", "bloat-free")
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_test_engine": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_test_engine": False
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if "testengine" not in self.conan_data["sources"][self.version]:
            self.output.warning("No test engine found for this version, removing test engine option")
            del self.options.enable_test_engine

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["core"], strip_root=True)
        if "testengine" in self.conan_data["sources"][self.version]:
            get(self, **self.conan_data["sources"][self.version]["testengine"], strip_root=True, destination="test_engine")
        self._patch_sources()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["IMGUI_SRC_DIR"] = self.source_folder.replace("\\", "/")
        # test engine is not available for all versions
        if self.options.get_safe("enable_test_engine"):
            tc.preprocessor_definitions["IMGUI_ENABLE_TEST_ENGINE"] = "1"
            tc.preprocessor_definitions["IMGUI_TEST_ENGINE_ENABLE_COROUTINE_STDTHREAD_IMPL"] = "1"
            tc.variables["IMGUI_ENABLE_TEST_ENGINE"] = "ON"
            tc.variables["IMGUI_TEST_ENGINE_DIR"] = os.path.join(self.source_folder, "test_engine").replace("\\", "/")
        tc.generate()

    def _patch_sources(self):
        # Ensure we take into account export_headers
        replace_in_file(self,
            os.path.join(self.source_folder, "imgui.h"),
            "#ifdef IMGUI_USER_CONFIG",
            "#include \"imgui_export_headers.h\"\n\n#ifdef IMGUI_USER_CONFIG"
        )

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        backends_folder = os.path.join(self.source_folder, "backends")
        copy(self, pattern="imgui_impl_*",
            dst=os.path.join(self.package_folder, "res", "bindings"),
            src=backends_folder)
        copy(self, pattern="imgui*.cpp",
            dst=os.path.join(self.package_folder, "res", "src"),
            src=os.path.join(self.source_folder))
        copy(self, pattern="*.*",
            dst=os.path.join(self.package_folder, "res", "misc", "cpp"),
            src=os.path.join(self.source_folder, "misc", "cpp"))
        copy(self, pattern="*.*",
            dst=os.path.join(self.package_folder, "res", "misc", "freetype"),
            src=os.path.join(self.source_folder, "misc", "freetype"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        _is_docking_branch = "docking" in str(self.version)
        self.conf_info.define("user.imgui:with_docking", _is_docking_branch)
        self.cpp_info.libs = ["imgui"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("imm32")
        self.cpp_info.srcdirs = [os.path.join("res", "bindings")]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
