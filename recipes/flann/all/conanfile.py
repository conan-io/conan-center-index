from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class FlannConan(ConanFile):
    name = "flann"
    description = "Fast Library for Approximate Nearest Neighbors"
    topics = ("flann", "nns", "nearest-neighbor-search", "knn", "kd-tree")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.cs.ubc.ca/research/flann/"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_hdf5": [True, False, "deprecated"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_hdf5": "deprecated",
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_hdf5 != "deprecated":
            self.output.warn("with_hdf5 is a deprecated option. Do not use.")

    @property
    def _min_cppstd(self):
        return 11 if tools.scm.Version(self, self.version) > "1.9.1" else None

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, self._min_cppstd)

    def requirements(self):
        self.requires("lz4/1.9.3")

    def package_id(self):
        del self.info.options.with_hdf5

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, {}):
            tools.files.patch(self, **patch)

        # remove embedded lz4
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "src", "cpp", "flann", "ext"))

        if tools.scm.Version(self, self.version) > "1.9.1":
            return

        # Workaround issue with empty sources for a CMake target
        flann_cpp_dir = os.path.join(self._source_subfolder, "src", "cpp")
        tools.files.save(self, os.path.join(flann_cpp_dir, "empty.cpp"), "\n")

        tools.files.replace_in_file(self, 
            os.path.join(flann_cpp_dir, "CMakeLists.txt"),
            'add_library(flann_cpp SHARED "")',
            'add_library(flann_cpp SHARED empty.cpp)'
        )
        tools.files.replace_in_file(self, 
            os.path.join(flann_cpp_dir, "CMakeLists.txt"),
            'add_library(flann SHARED "")',
            'add_library(flann SHARED empty.cpp)'
        )

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

        # Generate a relocatable shared lib on Macos
        self._cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

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
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # Remove vc runtimes
        if self.settings.os == "Windows":
            if self.options.shared:
                for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
                    tools.files.rm(self, 
                        os.path.join(self.package_folder, "bin"),
                        dll_pattern_to_remove,
                    )
            else:
                tools.files.rmdir(self, os.path.join(self.package_folder, "bin"))
        # Remove static/dynamic libraries depending on the build mode
        libs_pattern_to_remove = ["*flann_cpp_s.*", "*flann_s.*"] if self.options.shared else ["*flann_cpp.*", "*flann.*"]
        for lib_pattern_to_remove in libs_pattern_to_remove:
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), lib_pattern_to_remove)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "Flann")
        self.cpp_info.set_property("cmake_file_name", "flann")
        self.cpp_info.set_property("pkg_config_name", "flann")

        # flann_cpp
        flann_cpp_lib = "flann_cpp" if self.options.shared else "flann_cpp_s"
        self.cpp_info.components["flann_cpp"].set_property("cmake_target_name", "flann::{}".format(flann_cpp_lib))
        self.cpp_info.components["flann_cpp"].libs = [flann_cpp_lib]
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["flann_cpp"].system_libs.append(tools.stdcpp_library(self))
        self.cpp_info.components["flann_cpp"].requires = ["lz4::lz4"]

        # flann
        flann_c_lib = "flann" if self.options.shared else "flann_s"
        self.cpp_info.components["flann_c"].set_property("cmake_target_name", "flann::{}".format(flann_c_lib))
        self.cpp_info.components["flann_c"].libs = [flann_c_lib]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["flann_c"].system_libs.append("m")
        if not self.options.shared:
            self.cpp_info.components["flann_c"].defines.append("FLANN_STATIC")
        self.cpp_info.components["flann_c"].requires = ["flann_cpp"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Flann"
        self.cpp_info.names["cmake_find_package_multi"] = "flann"
        self.cpp_info.components["flann_cpp"].names["cmake_find_package"] = flann_cpp_lib
        self.cpp_info.components["flann_cpp"].names["cmake_find_package_multi"] = flann_cpp_lib
        self.cpp_info.components["flann_c"].names["cmake_find_package"] = flann_c_lib
        self.cpp_info.components["flann_c"].names["cmake_find_package_multi"] = flann_c_lib
