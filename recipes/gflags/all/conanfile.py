from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, rmdir, save
import os
import textwrap

required_conan_version = ">=1.47.0"


class GflagsConan(ConanFile):
    name = "gflags"
    description = "The gflags package contains a C++ library that implements commandline flags processing"
    topics = ("gflags", "cli", "flags", "commandline")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/gflags/gflags"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "nothreads": [True, False],
        "namespace": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "nothreads": True,
        "namespace": "gflags",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["BUILD_gflags_LIB"] = not self.options.nothreads
        tc.variables["BUILD_gflags_nothreads_LIB"] = self.options.nothreads
        tc.variables["BUILD_PACKAGING"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["INSTALL_HEADERS"] = True
        tc.variables["INSTALL_SHARED_LIBS"] = self.options.shared
        tc.variables["INSTALL_STATIC_LIBS"] = not self.options.shared
        tc.variables["REGISTER_BUILD_DIR"] = False
        tc.variables["REGISTER_INSTALL_PREFIX"] = False
        tc.variables["GFLAGS_NAMESPACE"] = self.options.namespace
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        #  TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"gflags": "gflags::gflags"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "gflags")
        self.cpp_info.set_property("cmake_target_name", "gflags::gflags")
        self.cpp_info.set_property("cmake_target_aliases", ["gflags"])
        self.cpp_info.set_property("pkg_config_name", "gflags")
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["shlwapi"])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m"])

        #  TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
