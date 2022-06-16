import os
import conan.tools.files
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import textwrap

required_conan_version = ">=1.29.1"


class IgnitionMathConan(ConanFile):
    name = "ignition-math"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gazebosim.org/libs/math"
    description = " Math classes and functions for robot applications"
    topics = ("ignition", "math", "robotics", "gazebo")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package_multi"
    exports_sources = "CMakeLists.txt", "patches/**"

    _cmake = None

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn(
                "{} recipe lacks information about the {} compiler support.".format(
                    self.name, self.settings.compiler
                )
            )
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires c++17 support. The current compiler {} {} does not support it.".format(
                        self.name,
                        self.settings.compiler,
                        self.settings.compiler.version,
                    )
                )

    def requirements(self):
        self.requires("eigen/3.3.9")
        self.requires("doxygen/1.8.17")
        self.requires("swig/4.0.2")

    def build_requirements(self):
        if int(tools.Version(self.version).minor) <= 8:
            self.build_requires("ignition-cmake/2.5.0")
        else:
            self.build_requires("ignition-cmake/2.10.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
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
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path),
            tools.Version(self.version))
        
        # Remove MS runtime files
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), dll_pattern_to_remove)

    @staticmethod
    def _create_cmake_module_variables(module_file, version):
        content = textwrap.dedent("""\
            set(ignition-math{major}_VERSION_MAJOR {major})
            set(ignition-math{major}_VERSION_MINOR {minor})
            set(ignition-math{major}_VERSION_PATCH {patch})
            set(ignition-math{major}_VERSION_STRING "{major}.{minor}.{patch}")
            set(ignition-math{major}_INCLUDE_DIRS "${{CMAKE_CURRENT_LIST_DIR}}/../../include/ignition/math{major}")
        """.format(major=version.major, minor=version.minor, patch=version.patch))
        tools.save(module_file, content)


    def package_info(self):
        version_major = tools.Version(self.version).major
        lib_name = f"ignition-math{version_major}"

        self.cpp_info.names["cmake_find_package"] = lib_name
        self.cpp_info.names["cmake_find_package_multi"] = lib_name
        self.cpp_info.names["cmake_paths"] = lib_name

        self.cpp_info.components[lib_name].names["cmake_find_package"] = lib_name
        self.cpp_info.components[lib_name].names["cmake_find_package_multi"] = lib_name
        self.cpp_info.components[lib_name].names["cmake_paths"] = lib_name
        self.cpp_info.components[lib_name].libs = [lib_name]
        self.cpp_info.components[lib_name].includedirs.append(os.path.join("include", "ignition", "math"+version_major))
        self.cpp_info.components[lib_name].requires = ["swig::swig", "eigen::eigen", "doxygen::doxygen"]

        self.cpp_info.components[lib_name].builddirs = [self._module_file_rel_dir]
        self.cpp_info.components[lib_name].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components[lib_name].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components[lib_name].build_modules["cmake_paths"] = [self._module_file_rel_path]

        self.cpp_info.components["eigen3"].names["cmake_find_package"] = "eigen3"
        self.cpp_info.components["eigen3"].names["cmake_find_package_multi"] = "eigen3"
        self.cpp_info.components["eigen3"].names["cmake_paths"] = "eigen3"
        self.cpp_info.components["eigen3"].includedirs.append(os.path.join("include", "ignition", "math"+version_major))
        self.cpp_info.components["eigen3"].requires = ["eigen::eigen"]

        self.cpp_info.components["eigen3"].builddirs = [self._module_file_rel_dir]
        self.cpp_info.components["eigen3"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["eigen3"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["eigen3"].build_modules["cmake_paths"] = [self._module_file_rel_path]
    
    def validate(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("sorry, M1 builds are not currently supported, give up!")
    
    @property
    def _module_file_rel_dir(self):
        return os.path.join("lib", "cmake")
    
    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_file_rel_dir, f"conan-official-{self.name}-variables.cmake")

