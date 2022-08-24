import os
from conans import CMake, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import conan.tools.files
import textwrap

required_conan_version = ">=1.29.1"


class IgnitionUitlsConan(ConanFile):
    name = "ignition-utils"
    license = "Apache-2.0"
    homepage = "https://gazebosim.org/libs/utils"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Provides general purpose classes and functions designed for robotic applications.."
    topics = ("ignition", "robotics", "utils")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], 
                "fPIC": [True, False],
                "ign_utils_vendor_cli11": [True, False]
              }
    default_options = {"shared": False, 
                       "fPIC": True,
                       "ign_utils_vendor_cli11": True
                       }
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

    def validate(self):
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("sorry, M1 builds are not currently supported, give up!")
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
        self.requires("doxygen/1.9.2")
        if self.options.ign_utils_vendor_cli11:
            self.requires("cli11/2.1.2")

    def build_requirements(self):
        self.build_requires("ignition-cmake/2.10.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["IGN_UTILS_VENDOR_CLI11"] = self.options.ign_utils_vendor_cli11
        self._cmake.definitions["CMAKE_FIND_DEBUG_MODE"] = "1"
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cli_header_src = os.path.join(self._source_subfolder, "cli", "include")
        if int(tools.Version(self.version).minor) == 0:
            cli_header_src = os.path.join(cli_header_src, "ignition", "utils", "cli")
        else:
            cli_header_src = os.path.join(cli_header_src, "external-cli", "ignition", "utils", "cli")
        self.copy("*.hpp", src=cli_header_src,
                     dst="include/ignition/utils1/ignition/utils/cli")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        # Remove MS runtime files
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), dll_pattern_to_remove)
        
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path),
            tools.Version(self.version)
        )

    @staticmethod
    def _create_cmake_module_variables(module_file, version):
        content = textwrap.dedent("""\
            set(ignition-utils{major}_VERSION_MAJOR {major})
            set(ignition-utils{major}_VERSION_MINOR {minor})
            set(ignition-utils{major}_VERSION_PATCH {patch})
            set(ignition-utils{major}_VERSION_STRING "{major}.{minor}.{patch}")
        """.format(major=version.major, minor=version.minor, patch=version.patch))
        tools.save(module_file, content)

    def package_info(self):
        version_major = tools.Version(self.version).major
        lib_name = f"ignition-utils{version_major}"
        build_dirs = os.path.join(self.package_folder, "lib", "cmake")
        include_dir = os.path.join("include", "ignition", "utils"+version_major)
        self.cpp_info.names["cmake_find_package"] = lib_name
        self.cpp_info.names["cmake_find_package_multi"] = lib_name
        self.cpp_info.names["cmake_paths"] = lib_name

        self.cpp_info.components[lib_name].names["cmake_find_package"] = lib_name
        self.cpp_info.components[lib_name].names["cmake_find_package_multi"] = lib_name
        self.cpp_info.components[lib_name].names["cmake_paths"] = lib_name
        self.cpp_info.components[lib_name].libs = [lib_name]
        self.cpp_info.components[lib_name].includedirs.append(include_dir)
        self.cpp_info.components[lib_name].requires = ["doxygen::doxygen"]
        if self.options.ign_utils_vendor_cli11:
            self.cpp_info.components[lib_name].requires.append("cli11::cli11")

        self.cpp_info.components[lib_name].builddirs.append(build_dirs)
        self.cpp_info.components[lib_name].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components[lib_name].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components[lib_name].build_modules["cmake_paths"] = [self._module_file_rel_path]

        self.cpp_info.components["cli"].names["cmake_find_package"] = "cli"
        self.cpp_info.components["cli"].names["cmake_find_package_multi"] = "cli"
        self.cpp_info.components["cli"].names["cmake_paths"] = "cli"
        self.cpp_info.components["cli"].includedirs.append(os.path.join(include_dir, "ignition", "utils"))
        if self.options.ign_utils_vendor_cli11:
            self.cpp_info.components["cli"].requires = ["cli11::cli11"]

        self.cpp_info.components["cli"].builddirs.append(build_dirs)
        self.cpp_info.components["cli"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["cli"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["cli"].build_modules["cmake_paths"] = [self._module_file_rel_path]

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")
