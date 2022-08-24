from conan import ConanFile, tools
from conans import CMake
import os
import textwrap

required_conan_version = ">=1.43.0"


class DocoptCppConan(ConanFile):
    name = "docopt.cpp"
    license = "MIT"
    description = "C++11 port of docopt"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/docopt/docopt.cpp"
    topics = ("cli", "getopt", "options", "argparser")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "boost_regex": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "boost_regex": False,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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

    def requirements(self):
        if self.options.boost_regex:
            self.requires("boost/1.76.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_BOOST_REGEX"] = self.options.boost_regex
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {self._cmake_target: "docopt::{}".format(self._cmake_target)}
        )

    @property
    def _cmake_target(self):
        return "docopt" if self.options.shared else "docopt_s"

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
        self.cpp_info.set_property("cmake_file_name", "docopt")
        self.cpp_info.set_property("cmake_target_name", self._cmake_target)
        self.cpp_info.set_property("pkg_config_name", "docopt")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["docopt"].libs = ["docopt"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["docopt"].system_libs = ["m"]
        if self._is_msvc and self.options.shared:
            self.cpp_info.components["docopt"].defines = ["DOCOPT_DLL"]
        if self.options.boost_regex:
            self.cpp_info.components["docopt"].requires.append("boost::boost")

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "docopt"
        self.cpp_info.names["cmake_find_package_multi"] = "docopt"
        self.cpp_info.names["pkg_config"] = "docopt"
        self.cpp_info.components["docopt"].names["cmake_find_package"] = self._cmake_target
        self.cpp_info.components["docopt"].names["cmake_find_package_multi"] = self._cmake_target
        self.cpp_info.components["docopt"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["docopt"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["docopt"].set_property("cmake_target_name", self._cmake_target)
