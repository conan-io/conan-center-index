from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.43.0"


class Bzip2Conan(ConanFile):
    name = "bzip2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.bzip.org"
    license = "bzip2-1.0.8"
    description = "bzip2 is a free and open-source file compression program that uses the Burrows Wheeler algorithm."
    topics = ("bzip2", "data-compressor", "file-compression")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_executable": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_executable": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.license = "bzip2-{}".format(self.version)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BZ2_VERSION_STRING"] = self.version
        self._cmake.definitions["BZ2_VERSION_MAJOR"] = tools.Version(self.version).major
        self._cmake.definitions["BZ2_BUILD_EXE"] = self.options.build_executable
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file):
        content = textwrap.dedent("""\
            set(BZIP2_NEED_PREFIX TRUE)
            if(NOT DEFINED BZIP2_FOUND AND DEFINED BZip2_FOUND)
                set(BZIP2_FOUND ${BZip2_FOUND})
            endif()
            if(NOT DEFINED BZIP2_INCLUDE_DIRS AND DEFINED BZip2_INCLUDE_DIRS)
                set(BZIP2_INCLUDE_DIRS ${BZip2_INCLUDE_DIRS})
            endif()
            if(NOT DEFINED BZIP2_INCLUDE_DIR AND DEFINED BZip2_INCLUDE_DIR)
                set(BZIP2_INCLUDE_DIR ${BZip2_INCLUDE_DIR})
            endif()
            if(NOT DEFINED BZIP2_LIBRARIES AND DEFINED BZip2_LIBRARIES)
                set(BZIP2_LIBRARIES ${BZip2_LIBRARIES})
            endif()
            if(NOT DEFINED BZIP2_VERSION_STRING AND DEFINED BZip2_VERSION)
                set(BZIP2_VERSION_STRING ${BZip2_VERSION})
            endif()
        """)
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-variables.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "BZip2")
        self.cpp_info.set_property("cmake_target_name", "BZip2::BZip2")
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.set_property("cmake_build_modules", [self._module_file])
        self.cpp_info.libs = ["bz2"]

        self.cpp_info.names["cmake_find_package"] = "BZip2"
        self.cpp_info.names["cmake_find_package_multi"] = "BZip2"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file]

        if self.options.build_executable:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
