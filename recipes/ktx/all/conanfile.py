from conan import ConanFile, tools
from conan.tools.cmake import CMake
import os

required_conan_version = ">=1.43.0"


class KtxConan(ConanFile):
    name = "ktx"
    description = "Khronos Texture library and tool."
    license = "Apache-2.0"
    topics = ("ktx", "texture", "khronos")
    homepage = "https://github.com/KhronosGroup/KTX-Software"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "sse": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "sse": True,
        "tools": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _has_sse_support(self):
        return self.settings.arch in ["x86", "x86_64"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_sse_support:
            del self.options.sse
        if self.settings.os in ["iOS", "Android", "Emscripten"]:
            # tools are not build by default if iOS, Android or Emscripten
            self.options.tools = False

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("lodepng/cci.20200615")
        self.requires("zstd/1.5.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        # Allow CMake wrapper
        tools.replace_in_file(cmakelists, "${CMAKE_SOURCE_DIR}", "${CMAKE_CURRENT_SOURCE_DIR}")
        tools.replace_in_file(cmakelists, "${CMAKE_BINARY_DIR}", "${CMAKE_CURRENT_BINARY_DIR}")
        # Unvendor several libs (we rely on CMake wrapper to link those libs)
        # It's worth noting that vendored jpeg-compressor can't be replaced by CCI equivalent
        basisu_dir = os.path.join(self.build_folder, self._source_subfolder, "lib", "basisu")
        ## lodepng (the patch file 0002-lodepng-no-export-symbols is important, in order to not try to export lodepng symbols)
        os.remove(os.path.join(basisu_dir, "encoder", "lodepng.cpp"))
        os.remove(os.path.join(basisu_dir, "encoder", "lodepng.h"))
        tools.replace_in_file(cmakelists, "lib/basisu/encoder/lodepng.cpp", "")
        tools.replace_in_file(cmakelists, "lib/basisu/encoder/lodepng.h", "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "tools", "toktx", "pngimage.cc"),
                              "#include \"encoder/lodepng.h\"",
                              "#include <lodepng.h>")
        ## zstd
        tools.rmdir(os.path.join(basisu_dir, "zstd"))
        tools.replace_in_file(cmakelists, "lib/basisu/zstd/zstd.c", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["KTX_FEATURE_TOOLS"] = self.options.tools
        self._cmake.definitions["KTX_FEATURE_DOC"] = False
        self._cmake.definitions["KTX_FEATURE_LOADTEST_APPS"] = False
        self._cmake.definitions["KTX_FEATURE_STATIC_LIBRARY"] = not self.options.shared
        self._cmake.definitions["KTX_FEATURE_TESTS"] = False
        self._cmake.definitions["BASISU_SUPPORT_SSE"] = self.options.get_safe("sse", False)
        self._cmake.configure()
        return self._cmake

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst="licenses", src=os.path.join(self._source_subfolder, "LICENSES"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Ktx")
        self.cpp_info.set_property("cmake_target_name", "KTX::ktx")

        self.cpp_info.filenames["cmake_find_package"] = "Ktx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Ktx"
        self.cpp_info.names["cmake_find_package"] = "KTX"
        self.cpp_info.names["cmake_find_package_multi"] = "KTX"
        self.cpp_info.components["libktx"].names["cmake_find_package"] = "ktx"
        self.cpp_info.components["libktx"].names["cmake_find_package_multi"] = "ktx"

        self.cpp_info.components["libktx"].libs = ["ktx"]
        self.cpp_info.components["libktx"].defines = [
            "KTX_FEATURE_KTX1", "KTX_FEATURE_KTX2", "KTX_FEATURE_WRITE"
        ]
        if not self.options.shared:
            self.cpp_info.components["libktx"].defines.append("KHRONOS_STATIC")
            stdcpp_library = tools.stdcpp_library(self)
            if stdcpp_library:
                self.cpp_info.components["libktx"].system_libs.append(stdcpp_library)
        if self.settings.os == "Windows":
            self.cpp_info.components["libktx"].defines.append("BASISU_NO_ITERATOR_DEBUG_LEVEL")
        elif self.settings.os == "Linux":
            self.cpp_info.components["libktx"].system_libs.extend(["m", "dl", "pthread"])
        self.cpp_info.components["libktx"].requires = ["lodepng::lodepng", "zstd::zstd"]

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
