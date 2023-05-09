from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import load, get, apply_conandata_patches, export_conandata_patches, rm, rmdir, copy, replace_in_file, save
from conan.tools.microsoft import msvc_runtime_flag, is_msvc
import os

required_conan_version = ">=1.53.0"

class PhysXConan(ConanFile):
    name = "physx"
    description = "The NVIDIA PhysX SDK is a scalable multi-platform " \
                  "physics solution supporting a wide range of devices, " \
                  "from smartphones to high-end multicore CPUs and GPUs."
    license = "BSD-3-Clause"
    topics = ("physx", "physics", "physics-engine", "physics-simulation", "game-development", "cuda")
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

    generators = "CMakeDeps"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

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
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.os not in ["Windows", "Linux", "Macos", "Android", "iOS"]:
            raise ConanInvalidConfiguration("Current os is not supported")

        if self.settings.os == "Macos" and self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration("{} only supports x86 and x86_64 on macOS".format(self.name))

        build_type = self.settings.build_type
        if build_type not in ["Debug", "RelWithDebInfo", "Release"]:
            raise ConanInvalidConfiguration("Current build_type is not supported")

        if self.settings.os == "Windows" and not is_msvc(self):
            raise ConanInvalidConfiguration("{} only supports Visual Studio on Windows".format(self.name))

        if is_msvc(self):
            allowed_runtimes = ["MDd", "MTd"] if build_type == "Debug" else ["MD", "MT"]
            if msvc_runtime_flag(self) not in allowed_runtimes:
                raise ConanInvalidConfiguration(
                    "Visual Studio runtime {0} is required for {1} build type".format(
                        " or ".join(allowed_runtimes),
                        build_type,
                    )
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        # Options defined in physx/compiler/public/CMakeLists.txt
        tc.cache_variables["TARGET_BUILD_PLATFORM"] = self._get_target_build_platform()
        tc.cache_variables["PX_BUILDSNIPPETS"] = False
        tc.cache_variables["PX_BUILDPUBLICSAMPLES"] = False
        tc.cache_variables["PX_CMAKE_SUPPRESS_REGENERATION"] = False
        cmakemodules_abspath = os.path.join(
            self.build_folder,
            self.source_folder,
            "externals",
            self._get_cmakemodules_subfolder()
        )
        tc.cache_variables["CMAKEMODULES_PATH"] = cmakemodules_abspath.replace("\\", "/")
        tc.cache_variables["PHYSX_ROOT_DIR"] = os.path.join(self.source_folder, "physx").replace("\\", "/")

        # Options defined in physx/source/compiler/cmake/CMakeLists.txt
        if self.settings.os in ["Windows", "Android"]:
            tc.cache_variables["PX_SCALAR_MATH"] = not self.options.enable_simd # this value doesn't matter on other os
        tc.cache_variables["PX_GENERATE_STATIC_LIBRARIES"] = not self.options.shared
        tc.cache_variables["PX_EXPORT_LOWLEVEL_PDB"] = False
        tc.cache_variables["PXSHARED_PATH"] = os.path.join(self.source_folder, "pxshared").replace("\\", "/")
        tc.cache_variables["PXSHARED_INSTALL_PREFIX"] = self.package_folder.replace("\\", "/")
        tc.cache_variables["PX_GENERATE_SOURCE_DISTRO"] = False

        # Options defined in externals/cmakemodules/NVidiaBuildOptions.cmake
        tc.cache_variables["NV_APPEND_CONFIG_NAME"] = False
        tc.cache_variables["NV_USE_GAMEWORKS_OUTPUT_DIRS"] = False
        if is_msvc(self):
            tc.cache_variables["NV_USE_STATIC_WINCRT"] = "MT" in msvc_runtime_flag(self)
            tc.cache_variables["NV_USE_DEBUG_WINCRT"] = "d" in msvc_runtime_flag(self)
        tc.cache_variables["NV_FORCE_64BIT_SUFFIX"] = False
        tc.cache_variables["NV_FORCE_32BIT_SUFFIX"] = False
        tc.cache_variables["PX_ROOT_LIB_DIR"] = os.path.join(self.package_folder, "lib").replace("\\", "/")

        if self.settings.os == "Windows":
            # Options defined in physx/source/compiler/cmake/windows/CMakeLists.txt
            tc.cache_variables["PX_COPY_EXTERNAL_DLL"] = False # External dll copy disabled, PhysXDevice dll copy is handled afterward during conan packaging
            tc.cache_variables["PX_FLOAT_POINT_PRECISE_MATH"] = self.options.enable_float_point_precise_math
            tc.cache_variables["PX_USE_NVTX"] = False # Could be controlled by an option if NVTX had a recipe, disabled for the moment
            tc.cache_variables["GPU_DLL_COPIED"] = True # PhysXGpu dll copy disabled, this copy is handled afterward during conan packaging

            # Options used in physx/source/compiler/cmake/windows/PhysX.cmake
            tc.cache_variables["PX_GENERATE_GPU_PROJECTS"] = False

        tc.generate()

    def build(self):
        self._patch_sources()

        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "physx/compiler/public"))
        cmake.build(build_type=self._get_physx_build_type())

    def _get_cmakemodules_subfolder(self):
        return "CMakeModules" if self.settings.os == "Windows" else "cmakemodules"

    def _patch_sources(self):
        apply_conandata_patches(self)

        # There is no reason to force consumer of PhysX public headers to use one of
        # NDEBUG or _DEBUG, since none of them relies on NDEBUG or _DEBUG
        replace_in_file(self, os.path.join(self.source_folder, "pxshared", "include", "foundation", "PxPreprocessor.h"),
                              "#error Exactly one of NDEBUG and _DEBUG needs to be defined!",
                              "// #error Exactly one of NDEBUG and _DEBUG needs to be defined!")

        physx_source_cmake_dir = os.path.join(self.source_folder, "physx", "source", "compiler", "cmake")

        # Remove global and specifics hard-coded PIC settings
        # (conan's CMake build helper properly sets CMAKE_POSITION_INDEPENDENT_CODE
        # depending on options)
        replace_in_file(self, os.path.join(physx_source_cmake_dir, "CMakeLists.txt"),
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
            replace_in_file(self, os.path.join(physx_source_cmake_dir, cmake_file),
                                  "SET_TARGET_PROPERTIES({} PROPERTIES POSITION_INDEPENDENT_CODE TRUE)".format(target),
                                  "")

        # No error for compiler warnings
        replace_in_file(self, os.path.join(physx_source_cmake_dir, "windows", "CMakeLists.txt"),
                              "/WX", "")
        for cmake_os in ("linux", "mac", "android", "ios"):
            replace_in_file(self, os.path.join(physx_source_cmake_dir, cmake_os, "CMakeLists.txt"),
                                  "-Werror", "")

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
        cmake = CMake(self)
        cmake.install(build_type=self._get_physx_build_type())

        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._get_license())

        cmake_installation_dir = os.path.join(self.package_folder, "lib", self._get_physx_build_type())
        package_dst_lib_dir = os.path.join(self.package_folder, "lib")
        package_dst_bin_dir = os.path.join(self.package_folder, "bin")

        copy(self, pattern="*.a", dst=package_dst_lib_dir, src=cmake_installation_dir, keep_path=False)
        copy(self, pattern="*.so", dst=package_dst_lib_dir, src=cmake_installation_dir, keep_path=False)
        copy(self, pattern="*.dylib*", dst=package_dst_lib_dir, src=cmake_installation_dir, keep_path=False)
        copy(self, pattern="*.lib", dst=package_dst_lib_dir, src=cmake_installation_dir, keep_path=False)
        copy(self, pattern="*.dll", dst=package_dst_bin_dir, src=cmake_installation_dir, keep_path=False)

        rmdir(self, os.path.join(self.package_folder, "source"))
        rmdir(self, cmake_installation_dir)

        self._copy_external_bin()

    def _get_license(self):
        readme = load(self, os.path.join(self.source_folder, "README.md"))
        begin = readme.find("Copyright")
        end = readme.find("\n## Introduction", begin)
        return readme[begin:end]

    def _copy_external_bin(self):
        # For Windows and Linux 64 bits, PhysXGpu (and PhysXDevice on Windows)
        # precompiled shared libs must also be provided to end-user if
        # application uses GPU features.
        external_bin_dir = os.path.join(self.source_folder, "physx", "bin")
        physx_build_type = self._get_physx_build_type()
        compiler_version = self.settings.compiler.version

        if self.settings.os == "Linux" and self.settings.arch == "x86_64":
            package_dst_lib_dir = os.path.join(self.package_folder, "lib")
            physx_gpu_dir = os.path.join(external_bin_dir, "linux.clang", physx_build_type)
            copy(self, pattern="*PhysXGpu*.so", dst=package_dst_lib_dir, src=physx_gpu_dir, keep_path=False)
        elif self.settings.os == "Windows" and is_msvc(self):
            physx_arch = {"x86": "x86_32", "x86_64": "x86_64"}.get(str(self.settings.arch))
            dll_info_list = [{
                "pattern": "PhysXGpu*.dll",
                "vc_ver": {"x86": "vc120", "x86_64": "vc140"}.get(str(self.settings.arch))
            }, {
                "pattern": "PhysXDevice*.dll",
                "vc_ver": {"180": "vc120", "190": "vc140", "191": "vc141"}.get(str(compiler_version), "vc142")
            }]
            
            package_dst_bin_dir = os.path.join(self.package_folder, "bin")

            for dll_info in dll_info_list:
                dll_subdir = "win.{0}.{1}.mt".format(physx_arch, dll_info.get("vc_ver"))
                dll_dir = os.path.join(external_bin_dir, dll_subdir, physx_build_type)
                copy(self, pattern=dll_info.get("pattern"), dst=package_dst_bin_dir, src=dll_dir, keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "PhysX")

        # PhysXFoundation
        self.cpp_info.components["physxfoundation"].set_property("cmake_target_name", "PhysX::PhysXFoundation")
        self.cpp_info.components["physxfoundation"].libs = ["PhysXFoundation"]
        if self.settings.os == "Linux":
            self.cpp_info.components["physxfoundation"].system_libs = ["m", "pthread", "rt"]
        elif self.settings.os == "Android":
            self.cpp_info.components["physxfoundation"].system_libs = ["log"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["physxfoundation"].system_libs = ["ws2_32"]

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
