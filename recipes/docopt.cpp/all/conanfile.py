from conan import ConanFile
from conan.tools.microsoft import is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, save
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os
import textwrap

required_conan_version = ">=1.53.0"

class DocoptCppConan(ConanFile):
    name = "docopt.cpp"
    description = "C++11 port of docopt"
    license = "MIT"
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

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.boost_regex:
            self.requires("boost/1.81.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_BOOST_REGEX"] = self.options.boost_regex
        tc.generate()

        dpes = CMakeDeps(self)
        dpes.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {self._cmake_target: "docopt::{}".format(self._cmake_target)}
        )

    @property
    def _cmake_target(self):
        return "docopt" if self.options.shared else "docopt_s"

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

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
        if is_msvc(self) and self.options.shared:
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
