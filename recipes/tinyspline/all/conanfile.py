from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir, save
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.50.0"


class TinysplineConan(ConanFile):
    name = "tinyspline"
    description = "Library for interpolating, transforming, and querying " \
                  "arbitrary NURBS, B-Splines, and Bezier curves."
    license = "MIT"
    topics = ("tinyspline ", "nurbs", "b-splines", "bezier")
    homepage = "https://github.com/msteinbeck/tinyspline"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cxx": [True, False],
        "floating_point_precision": ["double", "single"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cxx": True,
        "floating_point_precision": "double",
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.cxx:
            try:
               del self.settings.compiler.libcxx
            except Exception:
               pass
            try:
               del self.settings.compiler.cppstd
            except Exception:
               pass

    def validate(self):
        if Version(self.version) >= "0.4.0" and self.options.cxx:
            if self.info.settings.compiler.cppstd:
                check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TINYSPLINE_BUILD_DOCS"] = False
        tc.variables["TINYSPLINE_BUILD_EXAMPLES"] = False
        tc.variables["TINYSPLINE_BUILD_TESTS"] = False
        tc.variables["TINYSPLINE_FLOAT_PRECISION"] = self.options.floating_point_precision == "single"
        tc.variables["TINYSPLINE_INSTALL_BINARY_DIR"] = "bin"
        tc.variables["TINYSPLINE_INSTALL_LIBRARY_DIR"] = "lib"
        if Version(self.version) < "0.3.0":
            tc.variables["TINYSPLINE_DISABLE_CXX"] = not self.options.cxx
            tc.variables["TINYSPLINE_DISABLE_CSHARP"] = True
            tc.variables["TINYSPLINE_DISABLE_D"] = True
            tc.variables["TINYSPLINE_DISABLE_GOLANG"] = True
            tc.variables["TINYSPLINE_DISABLE_JAVA"] = True
            tc.variables["TINYSPLINE_DISABLE_LUA"] = True
            tc.variables["TINYSPLINE_DISABLE_OCTAVE"] = True
            tc.variables["TINYSPLINE_DISABLE_PHP"] = True
            tc.variables["TINYSPLINE_DISABLE_PYTHON"] = True
            tc.variables["TINYSPLINE_DISABLE_R"] = True
            tc.variables["TINYSPLINE_DISABLE_RUBY"] = True
        else:
            tc.variables["TINYSPLINE_WARNINGS_AS_ERRORS"] = False
            tc.variables["TINYSPLINE_ENABLE_CXX"] = self.options.cxx
            tc.variables["TINYSPLINE_ENABLE_CSHARP"] = False
            tc.variables["TINYSPLINE_ENABLE_DLANG"] = False
            tc.variables["TINYSPLINE_ENABLE_GO"] = False
            tc.variables["TINYSPLINE_ENABLE_JAVA"] = False
            tc.variables["TINYSPLINE_ENABLE_LUA"] = False
            tc.variables["TINYSPLINE_ENABLE_OCTAVE"] = False
            tc.variables["TINYSPLINE_ENABLE_PHP"] = False
            tc.variables["TINYSPLINE_ENABLE_PYTHON"] = False
            tc.variables["TINYSPLINE_ENABLE_R"] = False
            tc.variables["TINYSPLINE_ENABLE_RUBY"] = False
            tc.variables["TINYSPLINE_ENABLE_ALL_INTERFACES"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        if self.options.cxx:
            self._create_cmake_module_alias_targets(
                os.path.join(self.package_folder, self._module_file_rel_path),
                {"tinysplinecxx::tinysplinecxx": "tinyspline::libtinysplinecxx"}
            )

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
        if Version(self.version) < "0.3.0":
            lib_prefix = "lib" if is_msvc(self) and not self.options.shared else ""
            lib_suffix = "d" if is_msvc(self) and self.settings.build_type == "Debug" else ""
            cpp_prefix = "cpp"
        else:
            lib_prefix = ""
            lib_suffix = ""
            cpp_prefix = "cxx"

        self.cpp_info.set_property("cmake_file_name", "tinyspline")

        self.cpp_info.components["libtinyspline"].set_property("cmake_target_name", "tinyspline::tinyspline")
        self.cpp_info.components["libtinyspline"].set_property("pkg_config_name", "tinyspline")
        self.cpp_info.components["libtinyspline"].libs = ["{}tinyspline{}".format(lib_prefix, lib_suffix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libtinyspline"].system_libs = ["m"]
        if Version(self.version) >= "0.3.0" and self.options.shared and self.settings.os == "Windows":
            self.cpp_info.components["libtinyspline"].defines.append("TINYSPLINE_SHARED")

        if self.options.cxx:
            # FIXME: should live in tinysplinecxx-config.cmake (see https://github.com/conan-io/conan/issues/9000)
            self.cpp_info.components["libtinysplinecxx"].set_property("cmake_target_name", "tinysplinecxx::tinysplinecxx")
            self.cpp_info.components["libtinysplinecxx"].set_property("pkg_config_name", "tinysplinecxx")
            self.cpp_info.components["libtinysplinecxx"].libs = ["{}tinyspline{}{}".format(lib_prefix, cpp_prefix, lib_suffix)]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libtinysplinecxx"].system_libs = ["m"]
            if Version(self.version) >= "0.3.0" and self.options.shared and self.settings.os == "Windows":
                self.cpp_info.components["libtinysplinecxx"].defines.append("TINYSPLINE_SHARED")

            # Workaround to always provide a global target or pkg-config file with all components
            self.cpp_info.set_property("cmake_target_name", "tinyspline-do-not-use")
            self.cpp_info.set_property("pkg_config_name", "tinyspline-do-not-use")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libtinyspline"].names["cmake_find_package"] = "tinyspline"
        if self.options.cxx:
            self.cpp_info.components["libtinysplinecxx"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["libtinysplinecxx"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
