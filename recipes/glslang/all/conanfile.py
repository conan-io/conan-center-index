from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.32.0"


class GlslangConan(ConanFile):
    name = "glslang"
    description = "Khronos-reference front end for GLSL/ESSL, partial front " \
                  "end for HLSL, and a SPIR-V generator."
    license = ["BSD-3-Clause", "NVIDIA"]
    topics = ("conan", "glslang", "glsl", "hlsl", "spirv", "spir-v", "validation", "translation")
    homepage = "https://github.com/KhronosGroup/glslang"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_executables": [True, False],
        "spv_remapper": [True, False],
        "hlsl": [True, False],
        "enable_optimizer": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_executables": True,
        "spv_remapper": True,
        "hlsl": True,
        "enable_optimizer": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.options.shared and self.settings.os in ["Windows", "Macos"]:
            raise ConanInvalidConfiguration("Current glslang shared library build is broken on Windows and Macos")

    def requirements(self):
        if self.options.enable_optimizer:
            self.requires("spirv-tools/2020.5")

    def validate(self):
        if self.options.enable_optimizer and self.options["spirv-tools"].shared:
            raise ConanInvalidConfiguration("glslang with enable_optimizer requires static spirv-tools, because SPIRV-Tools-opt is not built if shared")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        self._patches_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patches_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Do not force PIC if static (but keep it if shared, because OGLCompiler and OSDependent are still static)
        if not self.options.shared:
            cmake_files_to_fix = [
                {"target": "OGLCompiler", "relpath": os.path.join("OGLCompilersDLL", "CMakeLists.txt")},
                {"target": "SPIRV"      , "relpath": os.path.join("SPIRV", "CMakeLists.txt")},
                {"target": "SPVRemapper", "relpath": os.path.join("SPIRV", "CMakeLists.txt")},
                {"target": "glslang"    , "relpath": os.path.join("glslang", "CMakeLists.txt")},
                {"target": "OSDependent", "relpath": os.path.join("glslang", "OSDependent", "Unix","CMakeLists.txt")},
                {"target": "OSDependent", "relpath": os.path.join("glslang", "OSDependent", "Windows","CMakeLists.txt")},
                {"target": "HLSL"       , "relpath": os.path.join("hlsl", "CMakeLists.txt")},
            ]
            for cmake_file in cmake_files_to_fix:
                tools.replace_in_file(os.path.join(self._source_subfolder, cmake_file["relpath"]),
                                      "set_property(TARGET {} PROPERTY POSITION_INDEPENDENT_CODE ON)".format(cmake_file["target"]),
                                      "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXTERNAL"] = False
        self._cmake.definitions["SKIP_GLSLANG_INSTALL"] = False
        self._cmake.definitions["ENABLE_SPVREMAPPER"] = self.options.spv_remapper
        self._cmake.definitions["ENABLE_GLSLANG_BINARIES"] = self.options.build_executables
        if tools.Version(self.version) >= "8.13.3743":
            self._cmake.definitions["ENABLE_GLSLANG_JS"] = False
            self._cmake.definitions["ENABLE_GLSLANG_WEBMIN"] = False
            self._cmake.definitions["ENABLE_GLSLANG_WEBMIN_DEVEL"] = False
        else:
            self._cmake.definitions["ENABLE_GLSLANG_WEB"] = False
            self._cmake.definitions["ENABLE_GLSLANG_WEB_DEVEL"] = False
        self._cmake.definitions["ENABLE_EMSCRIPTEN_SINGLE_FILE"] = False
        self._cmake.definitions["ENABLE_EMSCRIPTEN_ENVIRONMENT_NODE"] = False
        self._cmake.definitions["ENABLE_HLSL"] = self.options.hlsl
        if tools.Version(self.version) >= "8.13.3743":
            self._cmake.definitions["ENABLE_RTTI"] = False
        self._cmake.definitions["ENABLE_OPT"] = self.options.enable_optimizer
        self._cmake.definitions["ENABLE_PCH"] = True
        self._cmake.definitions["ENABLE_CTEST"] = False
        self._cmake.definitions["USE_CCACHE"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # TODO: glslang exports non-namespaced targets but without config file...
        lib_suffix = "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""
        # OSDependent
        self.cpp_info.components["osdependent"].names["cmake_find_package"] = "OSDependent"
        self.cpp_info.components["osdependent"].names["cmake_find_package_multi"] = "OSDependent"
        self.cpp_info.components["osdependent"].libs = ["OSDependent" + lib_suffix]
        if self.settings.os == "Linux":
            self.cpp_info.components["osdependent"].system_libs.append("pthread")
        # OGLCompiler
        self.cpp_info.components["oglcompiler"].names["cmake_find_package"] = "OGLCompiler"
        self.cpp_info.components["oglcompiler"].names["cmake_find_package_multi"] = "OGLCompiler"
        self.cpp_info.components["oglcompiler"].libs = ["OGLCompiler" + lib_suffix]
        # glslang
        self.cpp_info.components["glslang-core"].names["cmake_find_package"] = "glslang"
        self.cpp_info.components["glslang-core"].names["cmake_find_package_multi"] = "glslang"
        self.cpp_info.components["glslang-core"].libs = ["glslang" + lib_suffix]
        if self.settings.os == "Linux":
            self.cpp_info.components["glslang-core"].system_libs.extend(["m", "pthread"])
        self.cpp_info.components["glslang-core"].requires = ["oglcompiler", "osdependent"]
        # SPIRV
        self.cpp_info.components["spirv"].names["cmake_find_package"] = "SPIRV"
        self.cpp_info.components["spirv"].names["cmake_find_package_multi"] = "SPIRV"
        self.cpp_info.components["spirv"].libs = ["SPIRV" + lib_suffix]
        self.cpp_info.components["spirv"].requires = ["glslang-core"]
        if self.options.enable_optimizer:
            self.cpp_info.components["spirv"].requires.append("spirv-tools::spirv-tools-opt")
            self.cpp_info.components["spirv"].defines.append("ENABLE_OPT")
        # HLSL
        if self.options.hlsl:
            self.cpp_info.components["hlsl"].names["cmake_find_package"] = "HLSL"
            self.cpp_info.components["hlsl"].names["cmake_find_package_multi"] = "HLSL"
            self.cpp_info.components["hlsl"].libs = ["HLSL" + lib_suffix]
            self.cpp_info.components["glslang-core"].requires.append("hlsl")
            self.cpp_info.components["glslang-core"].defines.append("ENABLE_HLSL")
        # SPVRemapper
        if self.options.spv_remapper:
            self.cpp_info.components["spvremapper"].names["cmake_find_package"] = "SPVRemapper"
            self.cpp_info.components["spvremapper"].names["cmake_find_package_multi"] = "SPVRemapper"
            self.cpp_info.components["spvremapper"].libs = ["SPVRemapper" + lib_suffix]

        if self.options.build_executables:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
