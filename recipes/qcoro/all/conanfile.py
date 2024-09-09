import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, replace_in_file, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.56.0 <2 || >=2.0.6"


class QCoroConan(ConanFile):
    name = "qcoro"
    description = "C++ Coroutines for Qt."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/danvratil/qcoro"
    topics = ("coroutines", "qt")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "asan": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "asan": False,
    }

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "17",
            "msvc": "192",
            "clang": "8",
            "apple-clang": "13",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/[>=6.6.0 <7]", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 20)

        # Special check for clang that can only be linked to libc++
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration(
                "qcoro requires some C++20 features, which are only available in libc++ for clang compiler."
            )

        compiler_version = str(self.settings.compiler.version)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(compiler_version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"qcoro requires some C++20 features, which your {str(self.settings.compiler)} "
                f"{compiler_version} compiler does not support."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.23 <4]")
        self.tool_requires("qt/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _with_qml(self):
        return self.dependencies["qt"].options.get_safe("qtdeclarative", False)

    @property
    def _with_dbus(self):
        return self.dependencies["qt"].options.get_safe("with_dbus", False)

    @property
    def _with_quick(self):
        return (self.dependencies["qt"].options.get_safe("gui", False) and
                self.dependencies["qt"].options.get_safe("qtshadertools", False))

    @property
    def _with_websockets(self):
        return self.dependencies["qt"].options.get_safe("qtwebsockets", False)

    def generate(self):
        VirtualBuildEnv(self).generate()
        # Required for Qt's moc and qtpaths
        VirtualRunEnv(self).generate(scope="build")
        tc = CMakeToolchain(self)
        tc.variables["QCORO_BUILD_EXAMPLES"] = False
        tc.variables["QCORO_ENABLE_ASAN"] = self.options.asan
        tc.variables["BUILD_TESTING"] = False
        tc.variables["USE_QT_VERSION"] = self.dependencies["qt"].ref.version.major
        tc.variables["QCORO_WITH_QML"] = self._with_qml
        tc.variables["QCORO_WITH_QTDBUS"] = self._with_qml
        tc.variables["QCORO_WITH_QTQUICK"] = self._with_quick
        tc.variables["QCORO_WITH_QTWEBSOCKETS"] = self._with_websockets
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "ECMQueryQt.cmake"),
                        "get_target_property(_qtpaths_executable Qt6::qtpaths LOCATION)",
                        "set(_qtpaths_executable qtpaths)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*",
             src=os.path.join(self.source_folder, "LICENSES"),
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "mkspecs"))
        for mask in ["Find*.cmake", "*Config*.cmake", "*-config.cmake", "*Targets*.cmake"]:
            rm(self, mask, self.package_folder, recursive=True)

    def package_info(self):
        qt_major = self.dependencies["qt"].ref.version.major
        name = f"QCoro{qt_major}"
        self.cpp_info.set_property("cmake_file_name", name)
        self.cpp_info.set_property("cmake_target_name", f"{name}::{name}")

        def _add_module(module_name, requires=None, interface=False):
            component = self.cpp_info.components[module_name.lower()]
            component.set_property("cmake_target_name", f"{name}::{module_name}")
            if not interface:
                component.libs = [f"{name}{module_name}"]
            component.includedirs.append(os.path.join("include", f"qcoro{qt_major}", "qcoro"))
            component.requires = requires or []
            # TODO: Legacy, to be removed on Conan 2.0
            component.names["cmake_find_package"] = module_name
            component.names["cmake_find_package_multi"] = module_name

        _add_module("Coro", interface=True)
        _add_module("Core", requires=["coro", "qt::qtCore"])
        _add_module("Network", requires=["coro", "core", "qt::qtCore", "qt::qtNetwork"])
        if is_apple_os(self):
            self.cpp_info.components["network"].frameworks = ["CFNetwork"]
        _add_module("Test", requires=["qt::qtTest"], interface=True)
        if self._with_dbus:
            _add_module("DBus", requires=["coro", "core", "qt::qtCore", "qt::qtDBus"])
        if self._with_qml:
            _add_module("Qml", requires=["coro", "qt::qtCore", "qt::qtQml"])
        if self._with_quick:
            _add_module("Quick", requires=["coro", "core", "qt::qtCore", "qt::qtGui", "qt::qtQuick"])
        if self._with_websockets:
            _add_module("WebSockets", requires=["coro", "core", "qt::qtCore", "qt::qtNetwork", "qt::qtWebSockets"])

        self.cpp_info.builddirs.append(os.path.join("lib", "cmake", f"{name}Coro"))
        macros_cmake_path = os.path.join("lib", "cmake", f"{name}Coro", "QCoroMacros.cmake")
        self.cpp_info.set_property("cmake_build_modules", [macros_cmake_path])

        # TODO: Legacy, to be removed on Conan 2.0
        self.cpp_info.names["cmake_find_package"] = name
        self.cpp_info.names["cmake_find_package_multi"] = name
        self.cpp_info.components["core"].build_modules["cmake_find_package"].append(macros_cmake_path)
        self.cpp_info.components["core"].build_modules["cmake_find_package_multi"].append(macros_cmake_path)
