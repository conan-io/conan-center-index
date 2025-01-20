import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd, can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0.9"


class QtADS(ConanFile):
    name = "qt-advanced-docking-system"
    description = (
        "Qt Advanced Docking System lets you create customizable layouts "
        "using a full featured window docking system similar to what is found "
        "in many popular integrated development environments (IDEs) such as "
        "Visual Studio."
    )
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/githubuser0xFFFF/Qt-Advanced-Docking-System"
    topics = ("qt", "gui")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _qt_major(self):
        return Version(self.dependencies["qt"].ref.version).major

    @property
    def _min_cppstd(self):
        if self._qt_major >= 6:
            return 17
        else:
            return 14

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/[>=6.0 <7]", transitive_headers=True, transitive_libs=True, run=can_run(self))

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

    def build_requirements(self):
        if not can_run(self):
            self.tool_requires("qt/<host_version>", options={"gui": False, "widgets": False})

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ADS_VERSION"] = self.version
        tc.variables["BUILD_EXAMPLES"] = "OFF"
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "gnu-lgpl-v2.1.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "license"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if Version(self.version) >= 4:
            name = f"qt{self._qt_major}advanceddocking"
            self.cpp_info.includedirs.append(os.path.join("include", name))
            lib_name = f"{name}d" if self.settings.build_type == "Debug" else name
        else:
            lib_name = "qtadvanceddocking"

        if self.options.shared:
            self.cpp_info.libs = [lib_name]
        else:
            self.cpp_info.defines.append("ADS_STATIC")
            self.cpp_info.libs = [f"{lib_name}_static"]
