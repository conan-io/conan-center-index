from conans import ConanFile, tools, CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class SpirvtoolsConan(ConanFile):
    name = "diligentgraphics-spirv-tools"
    homepage = "https://github.com/DiligentGraphics/SPIRV-Tools/"
    description = "Diligent fork. Create and optimize SPIRV shaders"
    topics = ("spirv", "spirv-v", "vulkan", "opengl", "opencl", "hlsl", "khronos", "diligent")
    url = "https://github.com/conan-io/conan-center-index"
    provides = "spirv-tools"
    deprecated = "spirv-tools"
    license = "Apache-2.0"

    settings = "os", "compiler", "arch", "build_type"
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

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
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

    def requirements(self):
        if not self._get_compatible_spirv_headers_version:
            raise ConanInvalidConfiguration("unknown diligentgraphics-spirv-headers version")
        self.requires("diligentgraphics-spirv-headers/{}".format(self._get_compatible_spirv_headers_version))

    @property
    def _get_compatible_spirv_headers_version(self):
        return {
            "cci.20211008": "cci.20211006",
        }.get(str(self.version), False)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def _validate_dependency_graph(self):
        if self.deps_cpp_info["diligentgraphics-spirv-headers"].version != self._get_compatible_spirv_headers_version:
            raise ConanInvalidConfiguration("diligentgraphics-spirv-tools {0} requires diligentgraphics-spirv-headers {1}"
                                            .format(self.version, self._get_compatible_spirv_headers_version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        cmake = CMake(self)

        # Required by the project's CMakeLists.txt
        cmake.definitions["SPIRV-Headers_SOURCE_DIR"] = self.deps_cpp_info["diligentgraphics-spirv-headers"].rootpath.replace("\\", "/")

        # There are some switch( ) statements that are causing errors
        # need to turn this off
        cmake.definitions["SPIRV_WERROR"] = False

        cmake.definitions["SKIP_SPIRV_TOOLS_INSTALL"] = False
        cmake.definitions["SPIRV_LOG_DEBUG"] = False
        cmake.definitions["SPIRV_SKIP_TESTS"] = True
        cmake.definitions["SPIRV_CHECK_CONTEXT"] = False
        cmake.definitions["SPIRV_BUILD_FUZZER"] = False
        cmake.definitions["SPIRV_SKIP_EXECUTABLES"] = not self.options.build_executables

        cmake.configure(build_folder=self._build_subfolder)
        self._cmake = cmake
        return self._cmake

    def build(self):
        self._validate_dependency_graph()
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # CMAKE_POSITION_INDEPENDENT_CODE was set ON for the entire
        # project in the lists file.
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "SPIRV-Tools"))
        tools.rmdir(os.path.join(self.package_folder, "SPIRV-Tools-link"))
        tools.rmdir(os.path.join(self.package_folder, "SPIRV-Tools-opt"))
        tools.rmdir(os.path.join(self.package_folder, "SPIRV-Tools-reduce"))
        tools.rmdir(os.path.join(self.package_folder, "SPIRV-Tools-lint"))

        if self.options.shared:
            for file_name in ["*SPIRV-Tools", "*SPIRV-Tools-opt", "*SPIRV-Tools-link", "*SPIRV-Tools-reduce"]:
                for ext in [".a", ".lib"]:
                    tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), file_name + ext)
        else:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*SPIRV-Tools-shared.dll")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*SPIRV-Tools-shared*")

        if self.options.shared:
            targets = {"SPIRV-Tools-shared": "diligentgraphics-spirv-tools::SPIRV-Tools"}
        else:
            targets = {
                "SPIRV-Tools": "diligentgraphics-spirv-tools::SPIRV-Tools", # before 2020.5, kept for conveniency
                "SPIRV-Tools-static": "diligentgraphics-spirv-tools::SPIRV-Tools",
                "SPIRV-Tools-opt": "diligentgraphics-spirv-tools::SPIRV-Tools-opt",
                "SPIRV-Tools-link": "diligentgraphics-spirv-tools::SPIRV-Tools-link",
                "SPIRV-Tools-reduce": "diligentgraphics-spirv-tools::SPIRV-Tools-reduce",
            }
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            targets,
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "SPIRV-Tools"
        self.cpp_info.filenames["cmake_find_package_multi"] = "SPIRV-Tools"
        self.cpp_info.names["pkg_config"] = "SPIRV-Tools-shared" if self.options.shared else "SPIRV-Tools"

        # SPIRV-Tools
        self.cpp_info.components["spirv-tools-core"].names["cmake_find_package"] = "SPIRV-Tools"
        self.cpp_info.components["spirv-tools-core"].names["cmake_find_package_multi"] = "SPIRV-Tools"
        self.cpp_info.components["spirv-tools-core"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["spirv-tools-core"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["spirv-tools-core"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["spirv-tools-core"].libs = ["SPIRV-Tools-shared" if self.options.shared else "SPIRV-Tools"]
        self.cpp_info.components["spirv-tools-core"].requires = ["diligentgraphics-spirv-headers::diligentgraphics-spirv-headers"]
        if self.options.shared:
            self.cpp_info.components["spirv-tools-core"].defines = ["SPIRV_TOOLS_SHAREDLIB"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["spirv-tools-core"].system_libs.extend(["m", "rt"])
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["spirv-tools-core"].system_libs.append(tools.stdcpp_library(self))

        # FIXME: others components should have their own CMake config file
        if not self.options.shared:
            # SPIRV-Tools-opt
            self.cpp_info.components["spirv-tools-opt"].names["cmake_find_package"] = "SPIRV-Tools-opt"
            self.cpp_info.components["spirv-tools-opt"].names["cmake_find_package_multi"] = "SPIRV-Tools-opt"
            self.cpp_info.components["spirv-tools-opt"].builddirs.append(self._module_subfolder)
            self.cpp_info.components["spirv-tools-opt"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-opt"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-opt"].libs = ["SPIRV-Tools-opt"]
            self.cpp_info.components["spirv-tools-opt"].requires = ["spirv-tools-core", "diligentgraphics-spirv-headers::diligentgraphics-spirv-headers"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["spirv-tools-opt"].system_libs.append("m")
            # SPIRV-Tools-link
            self.cpp_info.components["spirv-tools-link"].names["cmake_find_package"] = "SPIRV-Tools-link"
            self.cpp_info.components["spirv-tools-link"].names["cmake_find_package_multi"] = "SPIRV-Tools-link"
            self.cpp_info.components["spirv-tools-link"].builddirs.append(self._module_subfolder)
            self.cpp_info.components["spirv-tools-link"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-link"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-link"].libs = ["SPIRV-Tools-link"]
            self.cpp_info.components["spirv-tools-link"].requires = ["spirv-tools-core", "spirv-tools-opt"]
            # SPIRV-Tools-reduce
            self.cpp_info.components["spirv-tools-reduce"].names["cmake_find_package"] = "SPIRV-Tools-reduce"
            self.cpp_info.components["spirv-tools-reduce"].names["cmake_find_package_multi"] = "SPIRV-Tools-reduce"
            self.cpp_info.components["spirv-tools-reduce"].builddirs.append(self._module_subfolder)
            self.cpp_info.components["spirv-tools-reduce"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-reduce"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
            self.cpp_info.components["spirv-tools-reduce"].libs = ["SPIRV-Tools-reduce"]
            self.cpp_info.components["spirv-tools-reduce"].requires = ["spirv-tools-core", "spirv-tools-opt"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % bin_path)
        self.env_info.path.append(bin_path)
