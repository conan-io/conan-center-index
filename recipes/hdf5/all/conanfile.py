import glob
import os

from conans import CMake, ConanFile, tools


class LibHdf5Conan(ConanFile):
    name = "hdf5"
    description = "HDF5 is a data model, library, and file format for storing and managing data"
    topics = "conan", "hdf5"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://portal.hdfgroup.org/display/support"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "hl": [True, False],
        "with_zlib": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "hl": True,
        "with_zlib": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-hdf5-" + self.version.replace('.', '_')
        os.rename(extracted_dir, self._source_subfolder)

        # Strip the debug suffix from library names
        if tools.Version(self.version) < "1.10.6":
            suffix_var = "LIB_DEBUG_SUFFIX"
        else:
            suffix_var = "CMAKE_DEBUG_POSTFIX"
        for suffix in ["_D", "_debug"]:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "config", "cmake_ext_mod", "HDFMacros.cmake"),
                'set ({} "{}")'.format(suffix_var, suffix),
                'set ({} "")'.format(suffix_var)
            )

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)

        # Needed to avoid constructing the static libraries
        if tools.Version(self.version) >= "1.10.6":
            self._cmake.definitions["ONLY_SHARED_LIBS"] = self.options.shared

        # Build only necessary modules
        self._cmake.definitions["BUILD_TESTING"] = "OFF"
        self._cmake.definitions["HDF5_BUILD_CPP_LIB"] = "ON"
        self._cmake.definitions["HDF5_BUILD_EXAMPLES"] = "OFF"
        self._cmake.definitions["HDF5_BUILD_TOOLS"] = "OFF"
        # Modules depending on options
        self._cmake.definitions["HDF5_BUILD_HL_LIB"] = self.options.hl
        self._cmake.definitions["HDF5_ENABLE_Z_LIB_SUPPORT"] = self.options.with_zlib

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        # Copy license file
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

        # Remove packaging files & MS runtime files
        for dir_to_remove in [
            "cmake",
            os.path.join("lib", "pkgconfig"),
            "share"
        ]:
            tools.rmdir(os.path.join(self.package_folder, dir_to_remove))

        # Remove more useless files
        for file_to_remove in [
            # General files (KB-H013)
            "COPYING",
            "RELEASE.txt",
            "USING_HDF5_CMake.txt",
            "USING_HDF5_VS.txt",
            # MS runtime files (KB-H021)
            os.path.join("bin", "concrt140.dll"),
            os.path.join("bin", "msvcp140.dll"),
            os.path.join("bin", "vcruntime140.dll")
        ]:
            path = os.path.join(self.package_folder, file_to_remove)
            if os.path.isfile(path):
                os.remove(path)

        # Manually remove the .a/.lib files if we are building in shared mode
        if self.options.shared and tools.Version(self.version) < "1.10.6":
            wildcard_pattern = os.path.join(self.package_folder, "lib", "lib*")
            for extension in [".a", ".lib"]:
                for static_lib in glob.glob(wildcard_pattern + extension):
                    os.remove(static_lib)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "HDF5"
        self.cpp_info.names["cmake_find_package_multi"] = "HDF5"

        # Manually list the library names to avoid link order issues
        if self.options.hl:
            self.cpp_info.libs =  ["hdf5_hl_cpp", "hdf5_hl"]
        else:
            self.cpp_info.libs = []
        self.cpp_info.libs.extend(["hdf5_cpp", "hdf5"])

        # Fix names for Windows static libs (they expect a leading 'lib')
        if not self.options.shared and self.settings.os == "Windows":
            self.cpp_info.libs = ["lib" + libname for libname in self.cpp_info.libs]

        if self.options.shared:
            self.cpp_info.defines.append("H5_BUILT_AS_DYNAMIC_LIB")

        if self.settings.os != "Windows":
            self.cpp_info.system_libs.append("dl")
