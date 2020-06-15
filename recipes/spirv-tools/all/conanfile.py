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
        "shared": True,
        "fPIC": True
    }

    def requirements(self):
        self.requires("spirv-headers/1.5.1")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "SPIRV-Tools-" + self.version[1:]
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

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

        # SPIRV-Tools-shared is meant to be a shared-only c-only API for the library .
        # it is built by the original CMakeLists.txt file. It is the same
        # as the other libraries except only the C interface is exposed
        # This library is being removed because it is only causing confusion.
        # As a result, you are restricted to to using the C++ api only.
        for bin_file in glob.glob(os.path.join(self.package_folder, "bin", "*SPIRV-Tools-shared.dll")):
            os.remove(bin_file)
        for lib_file in glob.glob(os.path.join(self.package_folder, "lib", "*SPIRV-Tools-shared*")):
            os.remove(lib_file)

    def package_info(self):
        # TODO: set targets names when components available in conan
        self.cpp_info.names["cmake_find_package"] = "SPIRV-Tools"
        self.cpp_info.names["cmake_find_package_multi"] = "SPIRV-Tools"

        # The spirv-tools CMAKE builds a SPIRV-Tools-shared.so which is
        # apparantly only exports the C-interface of the library.
        # The test_package.c is used when testing the c_only option
        # The C-interface is ALWAYS built as a shared-object as per the original
        # CMakeLists.txt file
        self.cpp_info.libs.append("SPIRV-Tools-reduce")
        self.cpp_info.libs.append("SPIRV-Tools-link")
        self.cpp_info.libs.append("SPIRV-Tools-opt")
        self.cpp_info.libs.append("SPIRV-Tools")

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "rt"]) # m for SPIRV-Tools-opt, rt for SPIRV-Tools

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.path.append(bin_path)
