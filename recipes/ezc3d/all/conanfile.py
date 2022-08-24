from conan import ConanFile, tools
from conan.tools.cmake import CMake
import functools
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
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_MATRIX_FAST_ACCESSOR"] = True
        cmake.definitions["BINDER_PYTHON3"] = False
        cmake.definitions["BINDER_MATLAB"] = False
        if tools.Version(self.version) >= "1.4.3":
            cmake.definitions["BINDER_OCTAVE"] = False
        cmake.definitions["BUILD_EXAMPLE"] = False
        cmake.definitions["BUILD_DOC"] = False
        cmake.definitions["GET_OFFICIAL_DOCUMENTATION"] = False
        cmake.definitions["BUILD_TESTS"] = False
        cmake.configure()
        return cmake

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
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ezc3d")
        self.cpp_info.set_property("cmake_target_name", "ezc3d")

        self.cpp_info.names["cmake_find_package"] = "ezc3d"
        self.cpp_info.names["cmake_find_package_multi"] = "ezc3d"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        self.cpp_info.includedirs.append(os.path.join("include", "ezc3d"))
        lib_suffix = {"Debug": "_debug"}.get(str(self.settings.build_type), "")
        self.cpp_info.libs = ["ezc3d" + lib_suffix]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
