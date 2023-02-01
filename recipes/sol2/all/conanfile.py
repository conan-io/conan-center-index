import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy

required_conan_version = ">=1.53.0"


class Sol2Conan(ConanFile):
    name = "sol2"
    package_type = "header-library"
    description = "a C++ <-> Lua API wrapper with advanced features and top notch performance"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ThePhD/sol2"
    topics = ("lua", "c++", "bindings", "scripting")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    options = {
        "with_lua": ["lua", "luajit"]
    }

    default_options = {
        "with_lua": "lua"
    }

    def requirements(self):
        if self.options.with_lua == "lua":
            if self.version < "3.1.0":
                # v2.x.x & v3.0.x supports up to Lua 5.3
                self.requires("lua/5.3.6")
            else:
                self.requires("lua/5.4.4")
        elif self.options.with_lua == "luajit":
            self.requires("luajit/2.1.0-beta3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    @property
    def _compilers_minimum_version(self):
        # TODO: MSVC?
        if self.version < "3.0.0":
            return {
                "Visual Studio": "14",
                "gcc": "5",
                "clang": "3.2",
                "apple-clang": "4.3"
            }
        else:
            return {
                "Visual Studio": "15.7" if Version(self.version) < "3.3.0" else "16",
                "gcc": "7",
                "clang": "6",
                "apple-clang": "10",
            }

    @property
    def _min_cppstd(self):
        if self.version < "3.0.0":
            # v2.x.x only requires C++14
            return 14
        else:
            # v3.x.x and soon v4.x.x requires C++17
            return 17

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warning(f"{self.ref} requires C++{self._min_cppstd}. Your compiler is unknown. Assuming it supports C++{self._min_cppstd}.")
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd} or higher support standard. {self.settings.compiler} {self.settings.compiler.version} is not supported.")

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.version < "3.0.0":
            copy(self, "*", src=os.path.join(self.source_folder, "sol"), dst=os.path.join(self.package_folder, "include", "sol"))
            copy(self, "sol.hpp", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        else:
            copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
            copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "sol2")
        if self.options.with_lua == "lua":
            if self.dependencies["lua"].options.compile_as_cpp:
                self.cpp_info.defines.append("SOL_USING_CXX_LUA=1")
            self.cpp_info.requires.append("lua::lua")
        elif self.options.with_lua == "luajit":
            self.cpp_info.defines.append("SOL_LUAJIT")
            self.cpp_info.requires.append("luajit::luajit")
