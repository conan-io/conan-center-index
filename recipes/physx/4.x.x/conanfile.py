from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os
import shutil

required_conan_version = ">=1.43.0"


class PhysXConan(ConanFile):
    name = "physx"
    description = "The NVIDIA PhysX SDK is a scalable multi-platform " \
                  "physics solution supporting a wide range of devices, " \
                  "from smartphones to high-end multicore CPUs and GPUs."
    license = "BSD-3-Clause"
    topics = ("PhysX", "physics", "physics-engine", "physics-simulation", "game-development", "cuda")
    homepage = "https://github.com/NVIDIAGameWorks/PhysX"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "release_build_type": ["profile", "release"],
        "enable_simd": [True, False],
        "enable_float_point_precise_math": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "release_build_type": "release",
        "enable_simd": True,
        "enable_float_point_precise_math": False,
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

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.build_type != "Release":
            del self.options.release_build_type
        if self.settings.os != "Windows":
            del self.options.enable_float_point_precise_math
        if self.settings.os not in ["Windows", "Android"]:
            del self.options.enable_simd

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os not in ["Windows", "Linux", "Macos", "Android", "iOS"]:
            raise ConanInvalidConfiguration("Current os is not supported")

        if self.settings.os == "Macos" and self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration("{} only supports x86 and x86_64 on macOS".format(self.name))

        build_type = self.settings.build_type
        if build_type not in ["Debug", "RelWithDebInfo", "Release"]:
            raise ConanInvalidConfiguration("Current build_type is not supported")

        if self.settings.os == "Windows" and not self._is_msvc:
            raise ConanInvalidConfiguration("{} only supports Visual Studio on Windows".format(self.name))

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        self._copy_sources()
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

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
            "pxshared",
            os.path.join("externals", self._get_cmakemodules_subfolder()),
            os.path.join("physx", "compiler"),
            os.path.join("physx", "include"),
            os.path.join("physx", "source"),
        ]
        for subfolder in subfolders_to_copy:
            shutil.copytree(os.path.join(self.source_folder, self._source_subfolder, subfolder),
                            os.path.join(self._source_subfolder, subfolder))

    def _get_cmakemodules_subfolder(self):
        return "CMakeModules" if self.settings.os == "Windows" else "cmakemodules"

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        # There is no reason to force consumer of PhysX public headers to use one of
        # NDEBUG or _DEBUG, since none of them relies on NDEBUG or _DEBUG
        tools.replace_in_file(os.path.join(self._source_subfolder, "pxshared", "include", "foundation", "PxPreprocessor.h"),
                              "#error Exactly one of NDEBUG and _DEBUG needs to be defined!",
                              "// #error Exactly one of NDEBUG and _DEBUG needs to be defined!")

        physx_source_cmake_dir = os.path.join(self._source_subfolder, "physx", "source", "compiler", "cmake")

        # Remove global and specifics hard-coded PIC settings
        # (conan's CMake build helper properly sets CMAKE_POSITION_INDEPENDENT_CODE
        # depending on options)
        tools.replace_in_file(os.path.join(physx_source_cmake_dir, "CMakeLists.txt"),
                              "SET(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")
        for cmake_file in (
            "FastXml.cmake",
            "LowLevel.cmake",
            "LowLevelAABB.cmake",
            "LowLevelDynamics.cmake",
            "PhysX.cmake",
            "PhysXCharacterKinematic.cmake",
            "PhysXCommon.cmake",
            "PhysXCooking.cmake",
            "PhysXExtensions.cmake",
            "PhysXFoundation.cmake",
            "PhysXPvdSDK.cmake",
            "PhysXTask.cmake",
            "PhysXVehicle.cmake",
            "SceneQuery.cmake",
            "SimulationController.cmake",
        ):
            target, _ = os.path.splitext(os.path.basename(cmake_file))
            tools.replace_in_file(os.path.join(physx_source_cmake_dir, cmake_file),
                                  "SET_TARGET_PROPERTIES({} PROPERTIES POSITION_INDEPENDENT_CODE TRUE)".format(target),
                                  "")

        # No error for compiler warnings
        tools.replace_in_file(os.path.join(physx_source_cmake_dir, "windows", "CMakeLists.txt"),
                              "/WX", "")
        for cmake_os in ("linux", "mac", "android", "ios"):
            tools.replace_in_file(os.path.join(physx_source_cmake_dir, cmake_os, "CMakeLists.txt"),
                                  "-Werror", "")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self, build_type=self._get_physx_build_type())

        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)

        # Options defined in physx/compiler/public/CMakeLists.txt
        cmake.definitions["TARGET_BUILD_PLATFORM"] = self._get_target_build_platform()
        cmake.definitions["PX_BUILDSNIPPETS"] = False
        cmake.definitions["PX_BUILDPUBLICSAMPLES"] = False
        cmake.definitions["PX_CMAKE_SUPPRESS_REGENERATION"] = False
        cmakemodules_abspath = os.path.join(
            self.build_folder,
            self._source_subfolder,
            "externals",
            self._get_cmakemodules_subfolder()
        )
        cmake.definitions["CMAKEMODULES_PATH"] = cmakemodules_abspath.replace("\\", "/")
        cmake.definitions["PHYSX_ROOT_DIR"] = os.path.join(self.build_folder, self._source_subfolder, "physx").replace("\\", "/")

        # Options defined in physx/source/compiler/cmake/CMakeLists.txt
        if self.settings.os in ["Windows", "Android"]:
            cmake.definitions["PX_SCALAR_MATH"] = not self.options.enable_simd # this value doesn't matter on other os
        cmake.definitions["PX_GENERATE_STATIC_LIBRARIES"] = not self.options.shared
        cmake.definitions["PX_EXPORT_LOWLEVEL_PDB"] = False
        cmake.definitions["PXSHARED_PATH"] = os.path.join(self.build_folder, self._source_subfolder, "pxshared").replace("\\", "/")
        cmake.definitions["PXSHARED_INSTALL_PREFIX"] = self.package_folder.replace("\\", "/")
        cmake.definitions["PX_GENERATE_SOURCE_DISTRO"] = False

        # Options defined in externals/cmakemodules/NVidiaBuildOptions.cmake
        cmake.definitions["NV_APPEND_CONFIG_NAME"] = False
        cmake.definitions["NV_USE_GAMEWORKS_OUTPUT_DIRS"] = False
        if self._is_msvc:
            cmake.definitions["NV_USE_STATIC_WINCRT"] = "MT" in msvc_runtime_flag(self)
            cmake.definitions["NV_USE_DEBUG_WINCRT"] = "d" in msvc_runtime_flag(self)
        cmake.definitions["NV_FORCE_64BIT_SUFFIX"] = False
        cmake.definitions["NV_FORCE_32BIT_SUFFIX"] = False
        cmake.definitions["PX_ROOT_LIB_DIR"] = os.path.join(self.package_folder, "lib").replace("\\", "/")

        if self.settings.os == "Windows":
            # Options defined in physx/source/compiler/cmake/windows/CMakeLists.txt
            cmake.definitions["PX_COPY_EXTERNAL_DLL"] = False # External dll copy disabled, PhysXDevice dll copy is handled afterward during conan packaging
            cmake.definitions["PX_FLOAT_POINT_PRECISE_MATH"] = self.options.enable_float_point_precise_math
            cmake.definitions["PX_USE_NVTX"] = False # Could be controlled by an option if NVTX had a recipe, disabled for the moment
            cmake.definitions["GPU_DLL_COPIED"] = True # PhysXGpu dll copy disabled, this copy is handled afterward during conan packaging

            # Options used in physx/source/compiler/cmake/windows/PhysX.cmake
            cmake.definitions["PX_GENERATE_GPU_PROJECTS"] = False

        cmake.configure(
            build_folder=os.path.join(self.build_folder, self._build_subfolder),
            source_folder=os.path.join(self.build_folder),
        )
        return cmake

    def _get_physx_build_type(self):
        if self.settings.build_type == "Debug":
            return "debug"
        elif self.settings.build_type == "RelWithDebInfo":
            return "checked"
        elif self.settings.build_type == "Release":
            if self.options.release_build_type == "profile":
                return "profile"
            else:
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
        cmake = self._configure_cmake()
        cmake.install()

        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._get_license())

        out_lib_dir = os.path.join(self.package_folder, "lib", self._get_physx_build_type())
        self.copy(pattern="*.a", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.so", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.dylib*", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=out_lib_dir, keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src=out_lib_dir, keep_path=False)

        tools.rmdir(out_lib_dir)
        tools.rmdir(os.path.join(self.package_folder, "source"))

        self._copy_external_bin()

    def _get_license(self):
        readme = tools.load(os.path.join(self.source_folder, self._source_subfolder, "README.md"))
        begin = readme.find("Copyright")
        end = readme.find("\n## Introduction", begin)
        return readme[begin:end]

    def _copy_external_bin(self):
        # For Windows and Linux 64 bits, PhysXGpu (and PhysXDevice on Windows)
        # precompiled shared libs must also be provided to end-user if
        # application uses GPU features.
        external_bin_dir = os.path.join(self.source_folder, self._source_subfolder, "physx", "bin")
        physx_build_type = self._get_physx_build_type()
        compiler_version = tools.Version(self.settings.compiler.version)

        if self.settings.os == "Linux" and self.settings.arch == "x86_64":
            physx_gpu_dir = os.path.join(external_bin_dir, "linux.clang", physx_build_type)
            self.copy(pattern="*PhysXGpu*.so", dst="lib", src=physx_gpu_dir, keep_path=False)
        elif self.settings.os == "Windows" and \
             ((self.settings.compiler == "Visual Studio" and compiler_version >= "12") or \
              str(self.settings.compiler) == "msvc"):
            physx_arch = {"x86": "x86_32", "x86_64": "x86_64"}.get(str(self.settings.arch))
            dll_info_list = [{
                "pattern": "PhysXGpu*.dll",
                "vc_ver": {"x86": "vc120", "x86_64": "vc140"}.get(str(self.settings.arch))
            }, {
                "pattern": "PhysXDevice*.dll",
                "vc_ver": {"12": "vc120", "14": "vc140", "15": "vc141"}.get(str(compiler_version), "vc142")
            }]
            for dll_info in dll_info_list:
                dll_subdir = "win.{0}.{1}.mt".format(physx_arch, dll_info.get("vc_ver"))
                dll_dir = os.path.join(external_bin_dir, dll_subdir, physx_build_type)
                self.copy(pattern=dll_info.get("pattern"), dst="bin", src=dll_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PhysX")

        # PhysXFoundation
        self.cpp_info.components["physxfoundation"].set_property("cmake_target_name", "PhysX::PhysXFoundation")
        self.cpp_info.components["physxfoundation"].libs = ["PhysXFoundation"]
        if self.settings.os == "Linux":
            self.cpp_info.components["physxfoundation"].system_libs = ["m", "pthread", "rt"]
        elif self.settings.os == "Android":
            self.cpp_info.components["physxfoundation"].system_libs = ["log"]

        # PhysXCommon
        self.cpp_info.components["physxcommon"].set_property("cmake_target_name", "PhysX::PhysXCommon")
        self.cpp_info.components["physxcommon"].libs = ["PhysXCommon"]
        if self.settings.os == "Linux":
            self.cpp_info.components["physxcommon"].system_libs = ["m"]
        self.cpp_info.components["physxcommon"].requires = ["physxfoundation"]

        # PhysXPvdSDK
        self.cpp_info.components["physxpvdsdk"].set_property("cmake_target_name", "PhysX::PhysXPvdSDK")
        self.cpp_info.components["physxpvdsdk"].libs = ["PhysXPvdSDK"]
        self.cpp_info.components["physxpvdsdk"].requires = ["physxfoundation"]

        # PhysX
        self.cpp_info.components["physxmain"].set_property("cmake_target_name", "PhysX::PhysX")
        self.cpp_info.components["physxmain"].libs = ["PhysX"]
        if self.settings.os == "Linux":
            self.cpp_info.components["physxmain"].system_libs = ["m"]
            if self.settings.arch == "x86_64":
                self.cpp_info.components["physxmain"].system_libs.append("dl")
        self.cpp_info.components["physxmain"].requires = ["physxpvdsdk", "physxcommon", "physxfoundation"]

        # PhysXTask
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["physxtask"].set_property("cmake_target_name", "PhysX::PhysXTask")
            self.cpp_info.components["physxtask"].libs = ["PhysXTask"]
            self.cpp_info.components["physxmain"].requires.append("physxtask")

        # PhysXCharacterKinematic
        self.cpp_info.components["physxcharacterkinematic"].set_property("cmake_target_name", "PhysX::PhysXCharacterKinematic")
        self.cpp_info.components["physxcharacterkinematic"].libs = ["PhysXCharacterKinematic"]
        self.cpp_info.components["physxcharacterkinematic"].requires = ["physxfoundation", "physxcommon", "physxextensions"]

        # PhysXCooking
        self.cpp_info.components["physxcooking"].set_property("cmake_target_name", "PhysX::PhysXCooking")
        self.cpp_info.components["physxcooking"].libs = ["PhysXCooking"]
        if self.settings.os == "Linux":
            self.cpp_info.components["physxcooking"].system_libs = ["m"]
        self.cpp_info.components["physxcooking"].requires = ["physxfoundation", "physxcommon"]

        # PhysXVehicle
        self.cpp_info.components["physxvehicle"].set_property("cmake_target_name", "PhysX::PhysXVehicle")
        self.cpp_info.components["physxvehicle"].libs = ["PhysXVehicle"]
        self.cpp_info.components["physxvehicle"].requires = ["physxfoundation", "physxpvdsdk", "physxextensions"]

        # PhysXExtensions
        self.cpp_info.components["physxextensions"].set_property("cmake_target_name", "PhysX::PhysXExtensions")
        self.cpp_info.components["physxextensions"].libs = ["PhysXExtensions"]
        self.cpp_info.components["physxextensions"].requires = ["physxfoundation", "physxpvdsdk", "physxmain", "physxcommon"]

        # TODO: remove in conan v2 once cmake_find_package* removed
        self.cpp_info.names["cmake_find_package"] = "PhysX"
        self.cpp_info.names["cmake_find_package_multi"] = "PhysX"
        self.cpp_info.components["physxfoundation"].names["cmake_find_package"] = "PhysXFoundation"
        self.cpp_info.components["physxfoundation"].names["cmake_find_package_multi"] = "PhysXFoundation"
        self.cpp_info.components["physxcommon"].names["cmake_find_package"] = "PhysXCommon"
        self.cpp_info.components["physxcommon"].names["cmake_find_package_multi"] = "PhysXCommon"
        self.cpp_info.components["physxpvdsdk"].names["cmake_find_package"] = "PhysXPvdSDK"
        self.cpp_info.components["physxpvdsdk"].names["cmake_find_package_multi"] = "PhysXPvdSDK"
        self.cpp_info.components["physxmain"].names["cmake_find_package"] = "PhysX"
        self.cpp_info.components["physxmain"].names["cmake_find_package_multi"] = "PhysX"
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["physxtask"].names["cmake_find_package"] = "PhysXTask"
            self.cpp_info.components["physxtask"].names["cmake_find_package_multi"] = "PhysXTask"
        self.cpp_info.components["physxcharacterkinematic"].names["cmake_find_package"] = "PhysXCharacterKinematic"
        self.cpp_info.components["physxcharacterkinematic"].names["cmake_find_package_multi"] = "PhysXCharacterKinematic"
        self.cpp_info.components["physxcooking"].names["cmake_find_package"] = "PhysXCooking"
        self.cpp_info.components["physxcooking"].names["cmake_find_package_multi"] = "PhysXCooking"
        self.cpp_info.components["physxvehicle"].names["cmake_find_package"] = "PhysXVehicle"
        self.cpp_info.components["physxvehicle"].names["cmake_find_package_multi"] = "PhysXVehicle"
        self.cpp_info.components["physxextensions"].names["cmake_find_package"] = "PhysXExtensions"
        self.cpp_info.components["physxextensions"].names["cmake_find_package_multi"] = "PhysXExtensions"
