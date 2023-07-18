import os
import shutil

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, rmdir, copy, replace_in_file, patch, export_conandata_patches
from conan.tools.env import Environment
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc

required_conan_version = ">=1.53.0"

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

    @property
    def _source_subfolder(self):
        return "src"

    def layout(self):
        cmake_layout(self, src_folder=self._source_subfolder)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, self._source_subfolder))
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def generate(self):
        cmake = CMakeToolchain(self)
        if not self.options.shared:
            cmake.variables["PX_STATIC_LIBRARIES"] = 1
        cmake.variables["STATIC_WINCRT"] = is_msvc_static_runtime(self)

        cmake.variables["NV_CLOTH_ENABLE_CUDA"] = self.options.use_cuda
        cmake.variables["NV_CLOTH_ENABLE_DX11"] = self.options.use_dx11

        cmake.variables["TARGET_BUILD_PLATFORM"] = self._get_target_build_platform()

        cmake.generate()
        cmake = CMakeDeps(self)
        cmake.generate()

    def build(self):
        self._patch_sources()
        self._remove_samples()

        env = Environment()
        env.define("GW_DEPS_ROOT", os.path.abspath(self.source_folder))
        envvars = env.vars(self, scope="build")
        with envvars.apply():
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def validate(self):
        if self.settings.os not in ["Windows", "Linux", "Macos", "Android", "iOS"]:
            raise ConanInvalidConfiguration("Current os is not supported")

        build_type = self.settings.build_type
        if build_type not in ["Debug", "RelWithDebInfo", "Release"]:
            raise ConanInvalidConfiguration("Current build_type is not supported")

        if is_msvc(self) and Version(self.settings.compiler.version) < 9:
            raise ConanInvalidConfiguration("Visual Studio versions < 9 are not supported")

    def _configure_cmake(self):
        cmake = CMakeToolchain(self)
        if not self.options.shared:
            cmake.variables["PX_STATIC_LIBRARIES"] = 1
        cmake.variables["STATIC_WINCRT"] = is_msvc_static_runtime(self)

        cmake.variables["NV_CLOTH_ENABLE_CUDA"] = self.options.use_cuda
        cmake.variables["NV_CLOTH_ENABLE_DX11"] = self.options.use_dx11

        cmake.variables["TARGET_BUILD_PLATFORM"] = self._get_target_build_platform()

        return cmake

    def _remove_samples(self):
        rmdir(self, os.path.join(self.source_folder, "NvCloth", "samples"))

    def _patch_sources(self):
        # There is no reason to force consumer of PhysX public headers to use one of
        # NDEBUG or _DEBUG, since none of them relies on NDEBUG or _DEBUG
        replace_in_file(self, os.path.join(self.source_folder, "PxShared", "include", "foundation", "PxPreprocessor.h"),
                              "#error Exactly one of NDEBUG and _DEBUG needs to be defined!",
                              "// #error Exactly one of NDEBUG and _DEBUG needs to be defined!")
        shutil.copy(
            os.path.join(self.source_folder, "NvCloth/include/NvCloth/Callbacks.h"),
            os.path.join(self.source_folder, "NvCloth/include/NvCloth/Callbacks.h.origin")
        )
        for each_patch in self.conan_data["patches"][self.version]:
            patch(self, **each_patch)

        if self.settings.build_type == "Debug":
            shutil.copy(
                os.path.join(self.source_folder, "NvCloth/include/NvCloth/Callbacks.h"),
                os.path.join(self.source_folder, "NvCloth/include/NvCloth/Callbacks.h.patched")
            )
            shutil.copy(
                os.path.join(self.source_folder, "NvCloth/include/NvCloth/Callbacks.h.origin"),
                os.path.join(self.source_folder, "NvCloth/include/NvCloth/Callbacks.h")
            )

    def _get_build_type(self):
        if self.settings.build_type == "Debug":
            return "debug"
        if self.settings.build_type == "RelWithDebInfo":
            return "checked"
        if self.settings.build_type == "Release":
            return "release"
        raise ConanInvalidConfiguration("Invalid build type")

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
                os.path.join(self.source_folder, "NvCloth/include/NvCloth/Callbacks.h.patched"),
                os.path.join(self.source_folder, "NvCloth/include/NvCloth/Callbacks.h")
            )
        nvcloth_source_subfolder = self.source_folder
        nvcloth_build_subfolder = self.build_folder

        print(nvcloth_build_subfolder)

        copy(self, pattern="NvCloth/license.txt", dst="licenses", src=nvcloth_source_subfolder, keep_path=False)
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(nvcloth_source_subfolder, "NvCloth", "include"))
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(nvcloth_source_subfolder, "NvCloth", "extensions", "include"))
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(nvcloth_source_subfolder, "PxShared", "include"))
        copy(self, "*.a", dst=os.path.join(self.package_folder, "lib"), src=nvcloth_build_subfolder, keep_path=False)
        copy(self, "*.lib", dst=os.path.join(self.package_folder, "lib"), src=nvcloth_build_subfolder, keep_path=False)
        copy(self, "*.dylib*", dst=os.path.join(self.package_folder, "lib"), src=nvcloth_build_subfolder, keep_path=False)
        copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=nvcloth_build_subfolder, keep_path=False)
        copy(self, "*.so", dst=os.path.join(self.package_folder, "lib"), src=nvcloth_build_subfolder, keep_path=False)

    def package_info(self):
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

        self.cpp_info.includedirs = ['include']
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.bindirs = ['bin']

        if not self.options.shared:
            if self.settings.os in ("FreeBSD", "Linux"):
                self.cpp_info.system_libs.append("m")
