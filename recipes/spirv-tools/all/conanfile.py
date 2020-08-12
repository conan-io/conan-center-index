from conans import ConanFile, tools, CMake
import os
import glob


class SpirvtoolsConan(ConanFile):
    name = "spirv-tools"
    homepage = "https://github.com/KhronosGroup/SPIRV-Tools/"
    description = "Create and optimize SPIRV shaders"
    topics = ("conan", "spirv", "spirv-v", "vulkan", "opengl", "opencl", "hlsl", "khronos")
    url = "https://github.com/conan-io/conan-center-index"
    short_paths = True
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt"]
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        self.requires("spirv-headers/{}".format(self._get_compatible_spirv_headers_version()))

    def _get_compatible_spirv_headers_version(self):
        return "1.5.3" if tools.Version(self.version[1:]) >= "2020.2" else "1.5.1"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "SPIRV-Tools-" + self.version[1:]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        cmake = CMake(self)

        if self.options.shared and self.settings.compiler == "Visual Studio":
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True

        # Required by the project's CMakeLists.txt
        cmake.definitions["SPIRV-Headers_SOURCE_DIR"] = self.deps_cpp_info["spirv-headers"].rootpath

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
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
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
        # SPIRV-Tools-shared is meant to be a shared-only c-only API for the library .
        # it is built by the original CMakeLists.txt file. It is the same
        # as the other libraries except only the C interface is exposed
        # This library is being removed because it is only causing confusion.
        for bin_file in glob.glob(os.path.join(self.package_folder, "bin", "*SPIRV-Tools-shared.dll")):
            os.remove(bin_file)
        for lib_file in glob.glob(os.path.join(self.package_folder, "lib", "*SPIRV-Tools-shared*")):
            os.remove(lib_file)

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "SPIRV-Tools"
        # SPIRV-Tools
        self.cpp_info.components["spirv-tools-core"].names["cmake_find_package"] = "SPIRV-Tools"
        self.cpp_info.components["spirv-tools-core"].names["cmake_find_package_multi"] = "SPIRV-Tools"
        self.cpp_info.components["spirv-tools-core"].libs = ["SPIRV-Tools"]
        self.cpp_info.components["spirv-tools-core"].requires = ["spirv-headers::spirv-headers"]
        if self.settings.os == "Linux":
            self.cpp_info.components["spirv-tools-core"].system_libs.append("rt")
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["spirv-tools-core"].system_libs.append(tools.stdcpp_library(self))
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
