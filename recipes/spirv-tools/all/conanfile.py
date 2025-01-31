from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rmdir, save
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

    @property
    def _compilers_minimum_version(self):
        return {
            "17": {
                "apple-clang": "10",
                "clang": "7" if Version(self.version) >= "1.3.250" else "5",
                "gcc": "8" if Version(self.version) >= "1.3.250" else "7",
                "msvc": "191",
                "Visual Studio": "15",
            }
        }.get(self._min_cppstd, {})

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

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def build_requirements(self):
        if Version(self.version) >= "1.3.239":
            self.tool_requires("cmake/[>=3.17.2 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = CMakeToolchain(self)
        # BUILD_SHARED_LIBS is used if SPIRV_TOOLS_BUILD_STATIC is set to False
        tc.variables["SPIRV_TOOLS_BUILD_STATIC"] = False
        # Required by the project's CMakeLists.txt
        tc.variables["SPIRV-Headers_SOURCE_DIR"] = self.dependencies["spirv-headers"].package_folder.replace("\\", "/")
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

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        targets = {
            "SPIRV-Tools": "spirv-tools::SPIRV-Tools",
            "SPIRV-Tools-shared": "spirv-tools::SPIRV-Tools",
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
        self.cpp_info.set_property("pkg_config_name", "SPIRV-Tools")
        if self.options.shared:
            self.cpp_info.set_property("pkg_config_aliases", ["SPIRV-Tools-shared"])

        # SPIRV-Tools
        self.cpp_info.components["spirv-tools-core"].set_property("cmake_target_name", "SPIRV-Tools")
        self.cpp_info.components["spirv-tools-core"].set_property("cmake_target_aliases", ["SPIRV-Tools-shared" if self.options.shared else "SPIRV-Tools-static"])
        self.cpp_info.components["spirv-tools-core"].libs = ["SPIRV-Tools"]
        if self.options.shared:
            self.cpp_info.components["spirv-tools-core"].libs.append("SPIRV-Tools-shared")
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
        for lib in ["core", "opt", "link", "reduce", "lint", "diff"]:
            self.cpp_info.components[f"spirv-tools-{lib}"].names["cmake_find_package"] = f"SPIRV-Tools-{lib}"
            self.cpp_info.components[f"spirv-tools-{lib}"].names["cmake_find_package_multi"] = f"SPIRV-Tools-{lib}"
            self.cpp_info.components[f"spirv-tools-{lib}"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components[f"spirv-tools-{lib}"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        if Version(self.version) < "1.3":
            del self.cpp_info.components["spirv-tools-diff"]
