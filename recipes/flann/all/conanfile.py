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
            self.requires("hdf5/1.10.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

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

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, {}):
            tools.patch(**patch)
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
        if self.options.shared:
            self.cpp_info.libs = ["flann", "flann_cpp"]
        else:
            self.cpp_info.libs = ["flann_s", "flann_cpp_s"]

        if not self.options.shared:
            self.cpp_info.defines.append("FLANN_STATIC")
