import os
import shutil

from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import msvc_runtime_flag, is_msvc_static_runtime, is_msvc

required_conan_version = ">=1.35.0"

class NvclothConan(ConanFile):
    name = "nvcloth"
    license = "Nvidia Source Code License (1-Way Commercial)"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NVIDIAGameWorks/NvCloth"
    description = "NvCloth is a library that provides low level access to a cloth solver designed for realtime interactive applications."
    topics = ("physics", "physics-engine", "physics-simulation", "game-development", "cuda")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_cuda": [True, False],
        "use_dx11": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_cuda": False,
        "use_dx11": False
    }

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"
    
    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])
    
    def validate(self):
        if self.settings.os not in ["Windows", "Linux", "Macos", "Android", "iOS"]:
            raise ConanInvalidConfiguration("Current os is not supported")

        build_type = self.settings.build_type
        if build_type not in ["Debug", "RelWithDebInfo", "Release"]:
            raise ConanInvalidConfiguration("Current build_type is not supported")

        if is_msvc(self) and tools.Version(self.settings.compiler.version) < 9:
            raise ConanInvalidConfiguration("Visual Studio versions < 9 are not supported")

    def _configure_cmake(self):
        cmake = CMake(self)
        if not self.options.shared:
            cmake.definitions["PX_STATIC_LIBRARIES"] = 1
        cmake.definitions["STATIC_WINCRT"] = is_msvc_static_runtime(self)

        cmake.definitions["NV_CLOTH_ENABLE_CUDA"] = self.options.use_cuda
        cmake.definitions["NV_CLOTH_ENABLE_DX11"] = self.options.use_dx11

        cmake.definitions["TARGET_BUILD_PLATFORM"] = self._get_target_build_platform()

        cmake.configure(
            build_folder=os.path.join(self.build_folder, self._build_subfolder)
        )
        return cmake
    
    def _remove_samples(self):
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "NvCloth", "samples"))

    def _patch_sources(self):
        # There is no reason to force consumer of PhysX public headers to use one of
        # NDEBUG or _DEBUG, since none of them relies on NDEBUG or _DEBUG
        tools.files.replace_in_file(self, os.path.join(self.build_folder, self._source_subfolder, "PxShared", "include", "foundation", "PxPreprocessor.h"),
                              "#error Exactly one of NDEBUG and _DEBUG needs to be defined!",
                              "// #error Exactly one of NDEBUG and _DEBUG needs to be defined!")
        shutil.copy(
            os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h"),
            os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h.origin")
        )
        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)
        
        if self.settings.build_type == "Debug":
            shutil.copy(
                os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h"),
                os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h.patched")
            )
            shutil.copy(
                os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h.origin"),
                os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h")
            )
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build(self):
        with tools.environment_append({"GW_DEPS_ROOT": os.path.abspath(self._source_subfolder)}):
            self._patch_sources()
            self._remove_samples()
            cmake = self._configure_cmake()
            cmake.build()

    def _get_build_type(self):
        if self.settings.build_type == "Debug":
            return "debug"
        elif self.settings.build_type == "RelWithDebInfo":
            return "checked"
        elif self.settings.build_type == "Release":
            return "release"
    
    def _get_target_build_platform(self):
        return {
            "Windows" : "windows",
            "Linux" : "linux",
            "Macos" : "mac",
            "Android" : "android",
            "iOS" : "ios"
        }.get(str(self.settings.os))

    def package(self):
        if self.settings.build_type == "Debug":
            shutil.copy(
                os.path.join(self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h.patched"),
                os.path.join(self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h")
            )
        nvcloth_source_subfolder = os.path.join(self.build_folder, self._source_subfolder)
        nvcloth_build_subfolder = os.path.join(self.build_folder, self._build_subfolder)

        self.copy(pattern="NvCloth/license.txt", dst="licenses", src=nvcloth_source_subfolder, keep_path=False)
        self.copy("*.h", dst="include", src=os.path.join(nvcloth_source_subfolder, "NvCloth", "include"))
        self.copy("*.h", dst="include", src=os.path.join(nvcloth_source_subfolder, "NvCloth", "extensions", "include"))
        self.copy("*.h", dst="include", src=os.path.join(nvcloth_source_subfolder, "PxShared", "include"))
        self.copy("*.a", dst="lib", src=nvcloth_build_subfolder, keep_path=False)
        self.copy("*.lib", dst="lib", src=nvcloth_build_subfolder, keep_path=False)
        self.copy("*.dylib*", dst="lib", src=nvcloth_build_subfolder, keep_path=False)
        self.copy("*.dll", dst="bin", src=nvcloth_build_subfolder, keep_path=False)
        self.copy("*.so", dst="lib", src=nvcloth_build_subfolder, keep_path=False)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "nvcloth"
        self.cpp_info.names["cmake_find_package_multi"] = "nvcloth"

        if self.settings.build_type == "Debug":
            debug_suffix = "DEBUG"
        else:
            debug_suffix = ""

        if self.settings.os == "Windows":
            if self.settings.arch == "x86_64":
                arch_suffix = "x64"
            else:
                arch_suffix = ""
            self.cpp_info.libs = ["NvCloth{}_{}".format(debug_suffix, arch_suffix)]
        else:
            self.cpp_info.libs = ["NvCloth{}".format(debug_suffix)]

        if not self.options.shared:
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.system_libs.append("m")
