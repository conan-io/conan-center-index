from conans import ConanFile, tools, CMake
import os


class SpirvtoolsConan(ConanFile):
    name = "spirv-tools"
    homepage = "https://github.com/KhronosGroup/SPIRV-Tools/"
    description = "SPIRV-Tools "
    topics = ("conan", "spirv", "spirv-v", "vulkan", "opengl", "opencl", "hlsl", "khronos")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt"]
    license = "Apache-2.0"
    generators = "cmake"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "c_only": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "c_only": False
    }

    def requirements(self):
        self.requires.add("spirv-headers/1.5.1")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "SPIRV-Tools-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)

        # Required by the project's CMakeLists.txt
        cmake.definitions["SPIRV-Headers_SOURCE_DIR"] = self.deps_cpp_info["spirv-headers"].rootpath

        # There are some switch( ) statements that are causing errors
        # need to turn this off
        cmake.definitions["SPIRV_WERROR"] = False

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        # Error KB-H020, complaining that .pc files are found
        tools.rmdir(os.path.join(self.package_folder, "lib/pkgconfig"))

        # Error KB-H019, complaining that .pc files are found
        tools.rmdir(os.path.join(self.package_folder, "lib/cmake"))

    def package_info(self):
        # The spirv-tools CMAKE builds a SPIRV-Tools-shared.so which is
        # apparantly only exports the C-interface of the library.
        # The test_package.c is used when testing the c_only option
        # The C-interface is ALWAYS built as a shared-object as per the original
        # CMakeLists.txt file
        if self.options.c_only:
            self.cpp_info.libs.append("SPIRV-Tools-shared")
        else:
            self.cpp_info.libs.append("SPIRV-Tools-reduce")
            self.cpp_info.libs.append("SPIRV-Tools-link")
            self.cpp_info.libs.append("SPIRV-Tools-opt")
            self.cpp_info.libs.append("SPIRV-Tools")
