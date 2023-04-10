from conan import ConanFile
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.54.0"


class SpirvtoolsConan(ConanFile):
    name = "spirv-tools"
    homepage = "https://github.com/KhronosGroup/SPIRV-Tools/"
    description = "Create and optimize SPIRV shaders"
    topics = ("spirv", "spirv-v", "vulkan", "opengl", "opencl", "hlsl", "khronos")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_executables": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_executables": True,
    }

    short_paths = True

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "1.3.243" else "17"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"spirv-headers/{self.version}")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def _cmake_new_enough(self, required_version):
        try:
            import re
            from io import StringIO
            output = StringIO()
            self.run("cmake --version", output)
            m = re.search(r"cmake version (\d+\.\d+\.\d+)", output.getvalue())
            return Version(m.group(1)) >= required_version
        except:
            return False

    def build_requirements(self):
        if Version(self.version) >= "1.3.239":
            if not self._cmake_new_enough("3.17.2"):
                self.tool_requires("cmake/3.25.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)

        #====================
        # Shared libs mess in Spirv-Tools (see https://github.com/KhronosGroup/SPIRV-Tools/issues/3909)
        #====================
        # We have 2 solutions if shared True:
        #  - Only package SPIRV-Tools-shared lib (private symbols properly hidden), and wait resolution
        #    of above issue before allowing to build shared for all Spirv-Tools libs.
        #  - Build and package shared libs with all symbols exported
        #    (it would require CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS for msvc)
        # Currently this recipe implements the first solution

        # Static and shared libs are controlled by a weird combination
        # of SPIRV_TOOLS_BUILD_STATIC and BUILD_SHARED_LIBS.
        tc.variables["SPIRV_TOOLS_BUILD_STATIC"] = True
        #============

        # Required by the project's CMakeLists.txt
        tc.variables["SPIRV-Headers_SOURCE_DIR"] = self.dependencies["spirv-headers"].package_folder.replace("\\", "/")

        # There are some switch( ) statements that are causing errors
        # need to turn this off
        tc.variables["SPIRV_WERROR"] = False

        tc.variables["SKIP_SPIRV_TOOLS_INSTALL"] = False
        tc.variables["SPIRV_LOG_DEBUG"] = False
        tc.variables["SPIRV_SKIP_TESTS"] = True
        tc.variables["SPIRV_CHECK_CONTEXT"] = False
        tc.variables["SPIRV_BUILD_FUZZER"] = False
        tc.variables["SPIRV_SKIP_EXECUTABLES"] = not self.options.build_executables
        # To install relocatable shared libs on Macos
        if Version(self.version) < "1.3.239":
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        # For iOS/tvOS/watchOS
        tc.variables["CMAKE_MACOSX_BUNDLE"] = False

        tc.generate()

    def _patch_sources(self):
        # CMAKE_POSITION_INDEPENDENT_CODE was set ON for the entire
        # project in the lists file.
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "SPIRV-Tools"))
        rmdir(self, os.path.join(self.package_folder, "SPIRV-Tools-link"))
        rmdir(self, os.path.join(self.package_folder, "SPIRV-Tools-opt"))
        rmdir(self, os.path.join(self.package_folder, "SPIRV-Tools-reduce"))
        rmdir(self, os.path.join(self.package_folder, "SPIRV-Tools-lint"))
        rmdir(self, os.path.join(self.package_folder, "SPIRV-Tools-diff"))
        rmdir(self, os.path.join(self.package_folder, "SPIRV-Tools-tools"))
        if self.options.shared:
            for file_name in [
                "*SPIRV-Tools", "*SPIRV-Tools-opt", "*SPIRV-Tools-link",
                "*SPIRV-Tools-reduce", "*SPIRV-Tools-lint",
            ]:
                for ext in [".a", ".lib"]:
                    rm(self, f"{file_name}{ext}", os.path.join(self.package_folder, "lib"))
        else:
            rm(self, "*SPIRV-Tools-shared.dll", os.path.join(self.package_folder, "bin"))
            rm(self, "*SPIRV-Tools-shared*", os.path.join(self.package_folder, "lib"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        if self.options.shared:
            targets = {"SPIRV-Tools-shared": "spirv-tools::SPIRV-Tools"}
        else:
            targets = {
                "SPIRV-Tools": "spirv-tools::SPIRV-Tools", # before 2020.5, kept for conveniency
                "SPIRV-Tools-static": "spirv-tools::SPIRV-Tools",
                "SPIRV-Tools-opt": "spirv-tools::SPIRV-Tools-opt",
                "SPIRV-Tools-link": "spirv-tools::SPIRV-Tools-link",
                "SPIRV-Tools-reduce": "spirv-tools::SPIRV-Tools-reduce",
                "SPIRV-Tools-lint": "spirv-tools::SPIRV-Tools-lint",
                "SPIRV-Tools-diff": "spirv-tools::SPIRV-Tools-diff",
            }
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            targets,
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SPIRV-Tools")
        self.cpp_info.set_property("pkg_config_name", "SPIRV-Tools-shared" if self.options.shared else "SPIRV-Tools")

        # SPIRV-Tools
        self.cpp_info.components["spirv-tools-core"].set_property(
            "cmake_target_name",
            "SPIRV-Tools-shared" if self.options.shared else "SPIRV-Tools-static",
        )
        self.cpp_info.components["spirv-tools-core"].set_property("cmake_target_aliases", ["SPIRV-Tools"]) # before 2020.5, kept for conveniency
        self.cpp_info.components["spirv-tools-core"].libs = ["SPIRV-Tools-shared" if self.options.shared else "SPIRV-Tools"]
        self.cpp_info.components["spirv-tools-core"].requires = ["spirv-headers::spirv-headers"]
        if self.options.shared:
            self.cpp_info.components["spirv-tools-core"].defines = ["SPIRV_TOOLS_SHAREDLIB"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["spirv-tools-core"].system_libs.extend(["m", "rt"])
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["spirv-tools-core"].system_libs.append(libcxx)

        # FIXME: others components should have their own CMake config file
        if not self.options.shared:
            # SPIRV-Tools-opt
            self.cpp_info.components["spirv-tools-opt"].set_property("cmake_target_name", "SPIRV-Tools-opt")
            self.cpp_info.components["spirv-tools-opt"].libs = ["SPIRV-Tools-opt"]
            self.cpp_info.components["spirv-tools-opt"].requires = ["spirv-tools-core", "spirv-headers::spirv-headers"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["spirv-tools-opt"].system_libs.append("m")

            # SPIRV-Tools-link
            self.cpp_info.components["spirv-tools-link"].set_property("cmake_target_name", "SPIRV-Tools-link")
            self.cpp_info.components["spirv-tools-link"].libs = ["SPIRV-Tools-link"]
            self.cpp_info.components["spirv-tools-link"].requires = ["spirv-tools-core", "spirv-tools-opt"]

            # SPIRV-Tools-reduce
            self.cpp_info.components["spirv-tools-reduce"].set_property("cmake_target_name", "SPIRV-Tools-reduce")
            self.cpp_info.components["spirv-tools-reduce"].libs = ["SPIRV-Tools-reduce"]
            self.cpp_info.components["spirv-tools-reduce"].requires = ["spirv-tools-core", "spirv-tools-opt"]

            # SPIRV-Tools-lint
            self.cpp_info.components["spirv-tools-lint"].set_property("cmake_target_name", "SPIRV-Tools-lint")
            self.cpp_info.components["spirv-tools-lint"].libs = ["SPIRV-Tools-lint"]
            self.cpp_info.components["spirv-tools-lint"].requires = ["spirv-tools-core", "spirv-tools-opt"]

            # SPIRV-Tools-diff
            self.cpp_info.components["spirv-tools-diff"].set_property("cmake_target_name", "SPIRV-Tools-diff")
            self.cpp_info.components["spirv-tools-diff"].libs = ["SPIRV-Tools-diff"]
            self.cpp_info.components["spirv-tools-diff"].requires = ["spirv-tools-core", "spirv-tools-opt"]

        if self.options.build_executables:
            self.env_info.path.append(os.path.join(self.package_folder, "bin"))

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "SPIRV-Tools"
        self.cpp_info.filenames["cmake_find_package_multi"] = "SPIRV-Tools"
        self.cpp_info.names["pkg_config"] = "SPIRV-Tools-shared" if self.options.shared else "SPIRV-Tools"
        self.cpp_info.components["spirv-tools-core"].names["cmake_find_package"] = "SPIRV-Tools"
        self.cpp_info.components["spirv-tools-core"].names["cmake_find_package_multi"] = "SPIRV-Tools"
        self.cpp_info.components["spirv-tools-core"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["spirv-tools-core"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if not self.options.shared:
            self.cpp_info.components["spirv-tools-opt"].names["cmake_find_package"] = "SPIRV-Tools-opt"
            self.cpp_info.components["spirv-tools-opt"].names["cmake_find_package_multi"] = "SPIRV-Tools-opt"
            self.cpp_info.components["spirv-tools-opt"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-opt"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-link"].names["cmake_find_package"] = "SPIRV-Tools-link"
            self.cpp_info.components["spirv-tools-link"].names["cmake_find_package_multi"] = "SPIRV-Tools-link"
            self.cpp_info.components["spirv-tools-link"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-link"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-reduce"].names["cmake_find_package"] = "SPIRV-Tools-reduce"
            self.cpp_info.components["spirv-tools-reduce"].names["cmake_find_package_multi"] = "SPIRV-Tools-reduce"
            self.cpp_info.components["spirv-tools-reduce"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-reduce"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-lint"].names["cmake_find_package"] = "SPIRV-Tools-lint"
            self.cpp_info.components["spirv-tools-lint"].names["cmake_find_package_multi"] = "SPIRV-Tools-lint"
            self.cpp_info.components["spirv-tools-lint"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-lint"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-diff"].names["cmake_find_package"] = "SPIRV-Tools-diff"
            self.cpp_info.components["spirv-tools-diff"].names["cmake_find_package_multi"] = "SPIRV-Tools-diff"
            self.cpp_info.components["spirv-tools-diff"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-diff"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
