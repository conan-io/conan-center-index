import glob
import os

from conans import ConanFile, CMake, tools


class LibFlannConan(ConanFile):
    name = "flann"
    description = "Fast Library for Approximate Nearest Neighbors"
    topics = "conan", "flann"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.cs.ubc.ca/research/flann/"
    license = "BSD-3-Clause"
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_hdf5": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_hdf5": False
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def requirements(self):
        if self.options.with_hdf5:
            self.requires("hdf5/1.10.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        # Workaround issue with empty sources for a CMake target
        flann_cpp_dir = os.path.join(self._source_subfolder, "src", "cpp")
        with open(os.path.join(flann_cpp_dir, "empty.cpp"), "w") as fd:
            fd.write("\n")  # touch

        tools.replace_in_file(
            os.path.join(flann_cpp_dir, "CMakeLists.txt"),
            'add_library(flann_cpp SHARED "")',
            'add_library(flann_cpp SHARED empty.cpp)'
        )
        tools.replace_in_file(
            os.path.join(flann_cpp_dir, "CMakeLists.txt"),
            'add_library(flann SHARED "")',
            'add_library(flann SHARED empty.cpp)'
        )

    def _configure_cmake(self):
        cmake = CMake(self)

        # TODO: check options
        # Only build the C++ libraries
        cmake.definitions["BUILD_DOC"] = "OFF"
        cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["BUILD_TESTS"] = "OFF"
        cmake.definitions["BUILD_C_BINDINGS"] = "OFF"
        cmake.definitions["BUILD_MATLAB_BINDINGS"] = "OFF"
        cmake.definitions["BUILD_PYTHON_BINDINGS"] = "OFF"

        # Workaround issue with flann_cpp
        if self.settings.os == "Windows" and self.options.shared:
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

        # Remove pkg-config files
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # Remove MS runtime files (KB-H021)
        for file_to_remove in ["concrt140.dll", "msvcp140.dll", "vcruntime140.dll"]:
            path = os.path.join(self.package_folder, "bin", file_to_remove)
            if os.path.isfile(path):
                os.remove(path)

        # Remove static/dynamic libraries depending on the build mode
        if self.options.shared:
            for file_to_remove in glob.glob(os.path.join(self.package_folder, "lib", "flann_cpp_s*")):
                os.remove(file_to_remove)
        else:
            if self.settings.os != "Linux":
                tools.rmdir(os.path.join(self.package_folder, "bin"))
            else:
                for file_to_remove in glob.glob(os.path.join(self.package_folder, "lib", "*.so*")):
                    os.remove(file_to_remove)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "FLANN"
        self.cpp_info.names["cmake_find_package_multi"] = "FLANN"

        if self.options.shared:
            self.cpp_info.libs = ["flann_cpp"]
        else:
            self.cpp_info.libs = ["flann_cpp_s"]
