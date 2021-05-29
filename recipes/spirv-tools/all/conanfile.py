from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os
import glob

required_conan_version = ">=1.29.1"


class SpirvtoolsConan(ConanFile):
    name = "spirv-tools"
    homepage = "https://github.com/KhronosGroup/SPIRV-Tools/"
    description = "Create and optimize SPIRV shaders"
    topics = ("conan", "spirv", "spirv-v", "vulkan", "opengl", "opencl", "hlsl", "khronos")
    url = "https://github.com/conan-io/conan-center-index"
    short_paths = True
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    license = "Apache-2.0"
    generators = "cmake"
    _cmake = None

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _version(self):
        if self.version[0] == "v":
            return self.version[1:]
        return self.version

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        if not self._get_compatible_spirv_headers_version:
            raise ConanInvalidConfiguration("unknown spirv-headers version")
        self.requires("spirv-headers/{}".format(self._get_compatible_spirv_headers_version))

    @property
    def _get_compatible_spirv_headers_version(self):
        return {
            "2020.5": "1.5.4",
            "2020.3": "1.5.3",
            "2019.2": "1.5.1",
        }.get(str(self._version), False)

    def _validate_dependency_graph(self):
        if self.deps_cpp_info["spirv-headers"].version != self._get_compatible_spirv_headers_version:
            raise ConanInvalidConfiguration("spirv-tools {0} requires spirv-headers {1}"
                                            .format(self._version, self._get_compatible_spirv_headers_version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "SPIRV-Tools-" + self._version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        cmake = CMake(self)

        # - Before v2020.5, the shared lib is always built, but static libs might be built as shared
        #   with BUILD_SHARED_LIBS injection (which doesn't work due to symbols visibility, at least for msvc)
        # - From v2020.5, static and shared libs are fully controlled by upstream CMakeLists.txt
        if tools.Version(self._version) < "2020.5":
            cmake.definitions["BUILD_SHARED_LIBS"] = False

        # Required by the project's CMakeLists.txt
        cmake.definitions["SPIRV-Headers_SOURCE_DIR"] = self.deps_cpp_info["spirv-headers"].rootpath.replace("\\", "/")

        # There are some switch( ) statements that are causing errors
        # need to turn this off
        cmake.definitions["SPIRV_WERROR"] = False

        cmake.definitions["SKIP_SPIRV_TOOLS_INSTALL"] = False
        cmake.definitions["SPIRV_LOG_DEBUG"] = False
        cmake.definitions["SPIRV_SKIP_TESTS"] = True
        cmake.definitions["SPIRV_CHECK_CONTEXT"] = False
        cmake.definitions["SPIRV_BUILD_FUZZER"] = False

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
        if self.options.shared:
            for file_name in ["*SPIRV-Tools", "*SPIRV-Tools-opt", "*SPIRV-Tools-link", "*SPIRV-Tools-reduce"]:
                for ext in [".a", ".lib"]:
                    tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), file_name + ext)
        else:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*SPIRV-Tools-shared.dll")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*SPIRV-Tools-shared*")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "SPIRV-Tools-shared" if self.options.shared else "SPIRV-Tools"
        # FIXME: official CMake imported targets are not namespaced
        # SPIRV-Tools
        self.cpp_info.components["spirv-tools-core"].names["cmake_find_package"] = "SPIRV-Tools"
        self.cpp_info.components["spirv-tools-core"].names["cmake_find_package_multi"] = "SPIRV-Tools"
        self.cpp_info.components["spirv-tools-core"].libs = ["SPIRV-Tools-shared" if self.options.shared else "SPIRV-Tools"]
        self.cpp_info.components["spirv-tools-core"].requires = ["spirv-headers::spirv-headers"]
        if self.options.shared:
            self.cpp_info.components["spirv-tools-core"].defines = ["SPIRV_TOOLS_SHAREDLIB"]
        if self.settings.os == "Linux":
            self.cpp_info.components["spirv-tools-core"].system_libs.append("rt")
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["spirv-tools-core"].system_libs.append(tools.stdcpp_library(self))

        # Also provide official CMake imported target names for SPIRV-Tools lib:
        # - if shared: SPIRV-Tools-shared
        # - if static: SPIRV-Tools-static if version >= 2020.5 else SPIRV-Tools
        spirv_tools_target = "SPIRV-Tools-shared" if self.options.shared else "SPIRV-Tools-static"
        self.cpp_info.components["spirv-tools-core-alias"].names["cmake_find_package"] = spirv_tools_target
        self.cpp_info.components["spirv-tools-core-alias"].names["cmake_find_package_multi"] = spirv_tools_target

        # FIXME: others components should have their own CMake config file
        if not self.options.shared:
            # SPIRV-Tools-opt
            self.cpp_info.components["spirv-tools-opt"].names["cmake_find_package"] = "SPIRV-Tools-opt"
            self.cpp_info.components["spirv-tools-opt"].names["cmake_find_package_multi"] = "SPIRV-Tools-opt"
            self.cpp_info.components["spirv-tools-opt"].libs = ["SPIRV-Tools-opt"]
            self.cpp_info.components["spirv-tools-opt"].requires = ["spirv-tools-core", "spirv-headers::spirv-headers"]
            if self.settings.os == "Linux":
                self.cpp_info.components["spirv-tools-opt"].system_libs.append("m")
            # SPIRV-Tools-link
            self.cpp_info.components["spirv-tools-link"].names["cmake_find_package"] = "SPIRV-Tools-link"
            self.cpp_info.components["spirv-tools-link"].names["cmake_find_package_multi"] = "SPIRV-Tools-link"
            self.cpp_info.components["spirv-tools-link"].libs = ["SPIRV-Tools-link"]
            self.cpp_info.components["spirv-tools-link"].requires = ["spirv-tools-core", "spirv-tools-opt"]
            # SPIRV-Tools-reduce
            self.cpp_info.components["spirv-tools-reduce"].names["cmake_find_package"] = "SPIRV-Tools-reduce"
            self.cpp_info.components["spirv-tools-reduce"].names["cmake_find_package_multi"] = "SPIRV-Tools-reduce"
            self.cpp_info.components["spirv-tools-reduce"].libs = ["SPIRV-Tools-reduce"]
            self.cpp_info.components["spirv-tools-reduce"].requires = ["spirv-tools-core", "spirv-tools-opt"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % bin_path)
        self.env_info.path.append(bin_path)
