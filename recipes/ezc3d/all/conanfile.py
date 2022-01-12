from conans import ConanFile, CMake, tools
import os
import textwrap

required_conan_version = ">=1.43.0"


class Ezc3dConan(ConanFile):
    name = "ezc3d"
    description = "EZC3D is an easy to use reader, modifier and writer for C3D format files."
    license = "MIT"
    topics = ("ezc3d", "c3d")
    homepage = "https://github.com/pyomeca/ezc3d"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    _cmake = None

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

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
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # don't force PIC
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(CMAKE_POSITION_INDEPENDENT_CODE ON)", "")
        # fix install
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(${PROJECT_NAME}_LIB_FOLDER Lib",
                              "set(${PROJECT_NAME}_LIB_FOLDER lib")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(${PROJECT_NAME}_LIB_FOLDER lib/${PROJECT_NAME}",
                              "set(${PROJECT_NAME}_LIB_FOLDER lib")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set(${PROJECT_NAME}_BIN_FOLDER lib/${PROJECT_NAME}",
                              "set(${PROJECT_NAME}_BIN_FOLDER bin")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_MATRIX_FAST_ACCESSOR"] = True
        self._cmake.definitions["BINDER_PYTHON3"] = False
        self._cmake.definitions["BINDER_MATLAB"] = False
        self._cmake.definitions["BUILD_EXAMPLE"] = False
        self._cmake.definitions["BUILD_DOC"] = False
        self._cmake.definitions["GET_OFFICIAL_DOCUMENTATION"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "CMake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"ezc3d": "ezc3d::ezc3d"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ezc3d")
        self.cpp_info.set_property("cmake_target_name", "ezc3d")

        self.cpp_info.names["cmake_find_package"] = "ezc3d"
        self.cpp_info.names["cmake_find_package_multi"] = "ezc3d"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        self.cpp_info.includedirs.append(os.path.join("include", "ezc3d"))
        lib_suffix = {"Debug": "_debug"}.get(str(self.settings.build_type), "")
        self.cpp_info.libs = ["ezc3d" + lib_suffix]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
