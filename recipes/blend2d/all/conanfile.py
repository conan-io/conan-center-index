from conans import ConanFile, CMake, tools
import os
import glob

class Blend2dConan(ConanFile):
    name = "blend2d"
    license = "zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://blend2d.com/"
    description = "2D Vector Graphics Engine Powered by a JIT Compiler"
    topics = ("2d-graphics", "rasterization", "asmjit", "jit")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = ["CMakeLists.txt"]
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

    def requirements(self):
        self.requires("asmjit/cci.20220210")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BLEND2D_TEST"] = False
        self._cmake.definitions["BLEND2D_EMBED"] = False
        self._cmake.definitions["BLEND2D_STATIC"] = not self.options.shared
        self._cmake.configure()
        return self._cmake

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "  include(\"${ASMJIT_DIR}/CMakeLists.txt\")", "")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["blend2d"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "rt"])
