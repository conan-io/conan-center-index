import glob
import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class SpirvCrossConan(ConanFile):
    name = "spirv-cross"
    description = "SPIRV-Cross is a practical tool and library for performing " \
                  "reflection on SPIR-V and disassembling SPIR-V back to high level languages."
    license = "Apache-2.0"
    topics = ("conan", "spirv-cross", "reflection", "disassembler", "spirv", "spir-v", "glsl", "hlsl")
    homepage = "https://github.com/KhronosGroup/SPIRV-Cross"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_executable": [True, False],
        "glsl": [True, False],
        "hlsl": [True, False],
        "msl": [True, False],
        "cpp": [True, False],
        "reflect": [True, False],
        "c_api": [True, False],
        "util": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_executable": True,
        "glsl": True,
        "hlsl": True,
        "msl": True,
        "cpp": True,
        "reflect": True,
        "c_api": True,
        "util": True
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
        if not self.options.glsl and \
           (self.options.hlsl or self.options.msl or self.options.cpp or self.options.reflect):
            raise ConanInvalidConfiguration("hlsl, msl, cpp and reflect require glsl enabled")
        if self.options.shared:
            # these options don't contribute to shared binary
            del self.options.c_api
            del self.options.util

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = "SPIRV-Cross-" + os.path.basename(url).replace(".tar.gz", "").replace(".zip", "")
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        if self.options.build_executable and not self._are_proper_binaries_available_for_executable:
            self._build_exe()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SPIRV_CROSS_EXCEPTIONS_TO_ASSERTIONS"] = False
        self._cmake.definitions["SPIRV_CROSS_SHARED"] = self.options.shared
        self._cmake.definitions["SPIRV_CROSS_STATIC"] = not self.options.shared
        self._cmake.definitions["SPIRV_CROSS_CLI"] = self.options.build_executable and self._are_proper_binaries_available_for_executable
        self._cmake.definitions["SPIRV_CROSS_ENABLE_TESTS"] = False
        self._cmake.definitions["SPIRV_CROSS_ENABLE_GLSL"] = self.options.glsl
        self._cmake.definitions["SPIRV_CROSS_ENABLE_HLSL"] = self.options.hlsl
        self._cmake.definitions["SPIRV_CROSS_ENABLE_MSL"] = self.options.msl
        self._cmake.definitions["SPIRV_CROSS_ENABLE_CPP"] = self.options.cpp
        self._cmake.definitions["SPIRV_CROSS_ENABLE_REFLECT"] = self.options.reflect
        self._cmake.definitions["SPIRV_CROSS_ENABLE_C_API"] = self.options.get_safe("c_api", False)
        self._cmake.definitions["SPIRV_CROSS_ENABLE_UTIL"] = self.options.get_safe("util", False)
        self._cmake.definitions["SPIRV_CROSS_SKIP_INSTALL"] = False
        self._cmake.definitions["SPIRV_CROSS_FORCE_PIC"] = self.options.get_safe("fPIC", True)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    @property
    def _are_proper_binaries_available_for_executable(self):
        return (not self.options.shared and self.options.glsl and self.options.hlsl
                and self.options.msl and self.options.cpp and self.options.reflect
                and self.options.util)

    def _build_exe(self):
        cmake = CMake(self)
        cmake.definitions["SPIRV_CROSS_EXCEPTIONS_TO_ASSERTIONS"] = False
        cmake.definitions["SPIRV_CROSS_SHARED"] = False
        cmake.definitions["SPIRV_CROSS_STATIC"] = True
        cmake.definitions["SPIRV_CROSS_CLI"] = True
        cmake.definitions["SPIRV_CROSS_ENABLE_TESTS"] = False
        cmake.definitions["SPIRV_CROSS_ENABLE_GLSL"] = True
        cmake.definitions["SPIRV_CROSS_ENABLE_HLSL"] = True
        cmake.definitions["SPIRV_CROSS_ENABLE_MSL"] = True
        cmake.definitions["SPIRV_CROSS_ENABLE_CPP"] = True
        cmake.definitions["SPIRV_CROSS_ENABLE_REFLECT"] = True
        cmake.definitions["SPIRV_CROSS_ENABLE_C_API"] = False
        cmake.definitions["SPIRV_CROSS_ENABLE_UTIL"] = True
        cmake.definitions["SPIRV_CROSS_SKIP_INSTALL"] = True
        cmake.definitions["SPIRV_CROSS_FORCE_PIC"] = False
        cmake.configure(build_folder="build_subfolder_exe")
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        if self.options.build_executable and not self._are_proper_binaries_available_for_executable:
            self.copy(pattern="spirv-cross*", dst="bin", src=os.path.join("build_subfolder_exe", "bin"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug" and self.options.shared:
            for pdb_file in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
                os.remove(pdb_file)
            for ilk_file in glob.glob(os.path.join(self.package_folder, "bin", "*.ilk")):
                os.remove(ilk_file)

    def package_info(self):
        # TODO: set targets names when components available in conan
        self.cpp_info.libs = self._get_ordered_libs()
        self.cpp_info.includedirs.append(os.path.join("include", "spirv_cross"))
        if self.settings.os == "Linux" and self.options.glsl:
            self.cpp_info.system_libs.append("m")
        if self.options.build_executable:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

    def _get_ordered_libs(self):
        libs = []
        if self.options.shared:
            libs.append("spirv-cross-c-shared")
        else:
            # - spirv-cross-core is a dependency of spirv-cross-glsl and spirv-cross-util
            # - spirv-cross-glsl is a dependency of spirv-cross-c, spirv-cross-hlsl, spirv-cross-msl and spirv-cross-cpp
            # - spirv-cross-hlsl is a dependency of spirv-cross-c
            # - spirv-cross-msl is a dependency of spirv-cross-c
            # - spirv-cross-cpp is a dependency of spirv-cross-c
            # - spirv-cross-reflect is a dependency of spirv-cross-c
            if self.options.c_api:
                libs.append("spirv-cross-c")
            if self.options.hlsl:
                libs.append("spirv-cross-hlsl")
            if self.options.msl:
                libs.append("spirv-cross-msl")
            if self.options.cpp:
                libs.append("spirv-cross-cpp")
            if self.options.reflect:
                libs.append("spirv-cross-reflect")
            if self.options.glsl:
                libs.append("spirv-cross-glsl")
            if self.options.util:
                libs.append("spirv-cross-util")
            libs.append("spirv-cross-core")
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            libs = [lib + "d" for lib in libs]
        return libs
