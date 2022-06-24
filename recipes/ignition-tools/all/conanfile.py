import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import conan.tools.files
import textwrap

required_conan_version = ">=1.29.1"


class IgnitionToolsConan(ConanFile):
    name = "ignition-tools"
    license = "Apache-2.0"
    homepage = "https://gazebosim.org/libs/tools"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Provides general purpose classes and functions designed for robotic applications.."
    topics = ("ignition", "robotics", "tools")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package"
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
                f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support."
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

    def validate(self):
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) >= 11:
            raise ConanInvalidConfiguration("dependencies gmp/1.6.2 and ruby/3.1.0 are not available for this configuration")

    def requirements(self):
        self.requires("ruby/3.1.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], 
                strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake is not None:
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
        tools.rmdir(os.path.join(self.recipe_folder, "..", "source"))

        # Remove MS runtime files
        for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), dll_pattern_to_remove)

        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path),
                tools.Version(self.version))

    @staticmethod
    def _create_cmake_module_variables(module_file, version):
        content = textwrap.dedent("""\
            set(IGN_TOOLS_CONAN_PACKAGE_DIR ${{CMAKE_CURRENT_LIST_DIR/../..}})
            list(APPEND IGNITION-TOOLS_BINARY_DIRS ${{IGN_TOOLS_CONAN_PACKAGE_DIR}}/bin)
            list(APPEND IGNITION-TOOLS_INCLUDE_DIRS ${{IGN_TOOLS_CONAN_PACKAGE_DIR}}/include)
            list(APPEND IGNITION-TOOLS_LIBRARY_DIRS ${{IGN_TOOLS_CONAN_PACKAGE_DIR}}/libs)
            list(APPEND IGNITION-TOOLS_CFLAGS -I/${{IGN_TOOLS_CONAN_PACKAGE_DIR}}/include)
            list(APPEND IGNITION-TOOLS_CXX_FLAGS -std=c++11)
            set(ignition-tools{major}_VERSION_MAJOR {major})
            set(ignition-tools{major}_VERSION_MINOR {minor})
            set(ignition-tools{major}_VERSION_PATCH {patch})
            set(ignition-tools{major}_VERSION_STRING "{major}.{minor}.{patch}")
        """.format(major=version.major, minor=version.minor, patch=version.patch))
        tools.save(module_file, content)

    def package_info(self):
        lib_name = "ignition-tools"
        self.cpp_info.names["cmake_find_package"] = lib_name
        self.cpp_info.names["cmake_find_package_multi"] = lib_name
        self.cpp_info.names["cmake_paths"] = lib_name
        self.cpp_info.set_property("cmake_file_name", "ignition-tools")
        self.cpp_info.components["core"].names["cmake_find_package"] = "core"
        self.cpp_info.components["core"].names["cmake_find_package_multi"] = "core"
        self.cpp_info.components["core"].names["cmake_paths"] = "core"
        self.cpp_info.components["core"].bindirs = ["bin"]

        self.cpp_info.components["core"].libs = []
        self.cpp_info.components["core"].includedirs = []
        if int(tools.Version(self.version).minor) > 2:
            self.cpp_info.components["core"].libs.append(lib_name +"-backward")
            
        self.cpp_info.components["core"].requires = ["ruby::ruby"]

        self.cpp_info.components["core"].builddirs.append(self._module_dir_rel_path)
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.components["core"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["core"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["core"].build_modules["cmake_paths"] = [self._module_file_rel_path]

    @property
    def _module_dir_rel_path(self):
        return os.path.join("lib", "cmake")
    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_dir_rel_path, f"conan-official-{self.name}-variables.cmake")
