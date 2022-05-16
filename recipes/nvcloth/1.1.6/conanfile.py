import os
import shutil

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conan.tools.microsoft import msvc_runtime_flag

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
        "fPIC": False,
        "use_cuda": False,
        "use_dx11": False
    }

    no_copy_source = True
    short_paths = True

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"
    
    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

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

        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < 9:
            raise ConanInvalidConfiguration("Visual Studio versions < 9 are not supported")

        if self._is_msvc:
            allowed_runtimes = ["MDd", "MTd"] if build_type == "Debug" else ["MD", "MT"]
            if msvc_runtime_flag(self) not in allowed_runtimes:
                raise ConanInvalidConfiguration(
                    "Visual Studio runtime {0} is required for {1} build type".format(
                        " or ".join(allowed_runtimes),
                        build_type,
                    )
                )

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_BUILD_TYPE"]=self.settings.build_type
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", False)

        if not self.options.shared:
            cmake.definitions["PX_STATIC_LIBRARIES"] = "ON"

        if self._is_msvc and self.settings.compiler.runtime in ["MT", "MTd"]:
            cmake.definitions["STATIC_WINCRT"]="1"

        cmake.definitions["NV_CLOTH_ENABLE_CUDA"] = self.options.use_cuda
        cmake.definitions["NV_CLOTH_ENABLE_DX11"] = self.options.use_dx11

        cmake.definitions["TARGET_BUILD_PLATFORM"] = self._get_target_build_platform()

        cmake.configure(
            build_folder=os.path.join(self.build_folder, self._build_subfolder),
            source_folder=os.path.join(self.build_folder),
        )
        return cmake
    
    def _remove_samples(self):
        shutil.rmtree(os.path.join(self._source_subfolder, "NvCloth", "samples"))

    def _copy_sources(self):
        # Copy CMakeLists wrapper
        shutil.copy(os.path.join(self.source_folder, "CMakeLists.txt"), "CMakeLists.txt")

        # Copy patches
        if "patches" in self.conan_data and not os.path.exists("patches"):
            os.mkdir("patches")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            shutil.copy(os.path.join(self.source_folder, patch["patch_file"]), "patches")
        
        # Copy PhysX source code
        subfolders_to_copy = [
            "NvCloth",
            "PxShared",
        ]
        for subfolder in subfolders_to_copy:
            shutil.copytree(os.path.join(self.source_folder, self._source_subfolder, subfolder),
                            os.path.join(self._source_subfolder, subfolder))
    
    def _patch_sources(self):
        shutil.copy(
            os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h"),
            os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h.origin")
        )
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        
        if self.settings.build_type == "Debug":
            shutil.copy(
                os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h"),
                os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h.patched")
            )
            shutil.copy(
                os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h.origin"),
                os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h")
            )

    def build(self):
        os.environ['GW_DEPS_ROOT'] = os.path.abspath(self._source_subfolder)
        self._copy_sources()
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
                os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h.patched"),
                os.path.join(self.build_folder, self._source_subfolder, "NvCloth/include/NvCloth/Callbacks.h")
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
        self.cpp_info.libs = tools.collect_libs(self)
    
    def requirements(self):
        self.requires("physx/4.1.1")
