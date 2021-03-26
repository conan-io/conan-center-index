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
    exports_sources = ["CMakeLists.txt", "patches/**"]
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
        self.requires("lz4/1.9.2")
        if self.options.with_hdf5:
            self.requires("hdf5/1.12.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, {}):
            tools.patch(**patch)
        # Workaround issue with empty sources for a CMake target
        flann_cpp_dir = os.path.join(self._source_subfolder, "src", "cpp")
        tools.save(os.path.join(flann_cpp_dir, "empty.cpp"), "\n")

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
        # remove embeded lz4
        tools.rmdir(os.path.join(self._source_subfolder, "src", "cpp", "flann", "ext"))

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["BUILD_C_BINDINGS"] = True

        # Only build the C++ libraries
        self._cmake.definitions["BUILD_DOC"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_MATLAB_BINDINGS"] = False
        self._cmake.definitions["BUILD_PYTHON_BINDINGS"] = False

        # OpenMP support can be added later if needed
        self._cmake.definitions["USE_OPENMP"] = False

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # Remove static/dynamic libraries depending on the build mode
        if self.options.shared:
            # Remove MS runtime files
            for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
                for dll_to_remove in glob.glob(os.path.join(self.package_folder, "bin", dll_pattern_to_remove)):
                    os.remove(dll_to_remove)
        else:
            tools.rmdir(os.path.join(self.package_folder, "bin"))
        libs_pattern_to_remove = ["*flann_cpp_s.*", "*flann_s.*"] if self.options.shared else ["*flann_cpp.*", "*flann.*"]
        for lib_pattern_to_remove in libs_pattern_to_remove:
            for lib_to_remove in glob.glob(os.path.join(self.package_folder, "lib", lib_pattern_to_remove)):
                os.remove(lib_to_remove)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Flann"
        self.cpp_info.names["cmake_find_package_multi"] = "flann"
        # flann_cpp
        flann_cpp_lib = "flann_cpp" if self.options.shared else "flann_cpp_s"
        self.cpp_info.components["flann_cpp"].names["cmake_find_package"] = flann_cpp_lib
        self.cpp_info.components["flann_cpp"].names["cmake_find_package_multi"] = flann_cpp_lib
        self.cpp_info.components["flann_cpp"].libs = [flann_cpp_lib]
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["flann_cpp"].system_libs.append(tools.stdcpp_library(self))
        self.cpp_info.components["flann_cpp"].requires = ["lz4::lz4"]
        if self.options.with_hdf5:
            self.cpp_info.components["flann_cpp"].requires = ["hdf5::hdf5"]
        # flann
        flann_c_lib = "flann" if self.options.shared else "flann_s"
        self.cpp_info.components["flann_c"].names["cmake_find_package"] = flann_c_lib
        self.cpp_info.components["flann_c"].names["cmake_find_package_multi"] = flann_c_lib
        self.cpp_info.components["flann_c"].libs = [flann_c_lib]
        if self.settings.os == "Linux":
            self.cpp_info.components["flann_c"].system_libs.append("m")
        if not self.options.shared:
            self.cpp_info.components["flann_c"].defines.append("FLANN_STATIC")
        self.cpp_info.components["flann_c"].requires = ["flann_cpp"]
