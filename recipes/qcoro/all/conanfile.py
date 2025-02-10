import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, get, rm
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
        self.requires("qt/6.6.0", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 20)

        # Special check for clang that can only be linked to libc++
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration(
                "qcoro requires some C++20 features, which are available in libc++ for clang compiler."
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

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()
        # Required for Qt's moc
        venv = VirtualRunEnv(self)
        venv.generate(scope="build")
        tc = CMakeToolchain(self)
        tc.variables["QCORO_BUILD_EXAMPLES"] = False
        tc.variables["QCORO_ENABLE_ASAN"] = self.options.asan
        tc.variables["BUILD_TESTING"] = False
        tc.variables["QCORO_WITH_QTDBUS"] = self.dependencies["qt"].options.with_dbus
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*",
            dst=os.path.join(self.package_folder, "licenses"),
            src=os.path.join(self.source_folder, "LICENSES"))
        cmake = CMake(self)
        cmake.install()
        for mask in ["Find*.cmake", "*Config*.cmake", "*-config.cmake", "*Targets*.cmake"]:
            rm(self, mask, self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QCoro6")

        self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "QCoro6Coro"))
        macros_cmake_path = os.path.join("lib", "cmake", "QCoro6Coro", "QCoroMacros.cmake")
        self.cpp_info.set_property("cmake_build_modules", [macros_cmake_path])

        self.cpp_info.components["qcoro-core"].set_property("cmake_target_name", "QCoro::Core")
        self.cpp_info.components["qcoro-core"].libs = ["QCoro6Core"]
        self.cpp_info.components["qcoro-core"].includedirs.append(os.path.join("include", "qcoro6", "qcoro"))
        self.cpp_info.components["qcoro-core"].requires = ["qt::qtCore"]

        self.cpp_info.components["qcoro-network"].set_property("cmake_target_name", "QCoro::Network")
        self.cpp_info.components["qcoro-network"].libs = ["QCoro6Network"]
        self.cpp_info.components["qcoro-network"].requires = ["qt::qtNetwork"]
        if is_apple_os(self):
            self.cpp_info.components["qcoro-network"].frameworks = ["CFNetwork"]

        if self.dependencies["qt"].options.with_dbus:
            self.cpp_info.components["qcoro-dbus"].set_property("cmake_target_name", "QCoro::DBus")
            self.cpp_info.components["qcoro-dbus"].libs = ["QCoroDBus"]
            self.cpp_info.components["qcoro-core"].requires = ["qt::qtDBus"]

        # TODO: Legacy, to be removed on Conan 2.0
        self.cpp_info.filenames["cmake_find_package"] = "QCoro6"
        self.cpp_info.filenames["cmake_find_package_multi"] = "QCoro6"
        self.cpp_info.names["cmake_find_package"] = "QCoro"
        self.cpp_info.names["cmake_find_package_multi"] = "QCoro"
        self.cpp_info.components["qcoro-core"].names["cmake_find_package"] = "Core"
        self.cpp_info.components["qcoro-core"].names["cmake_find_package_multi"] = "Core"
        self.cpp_info.components["qcoro-network"].names["cmake_find_package"] = "Network"
        self.cpp_info.components["qcoro-network"].names["cmake_find_package_multi"] = "Network"
        if self.dependencies["qt"].options.with_dbus:
            self.cpp_info.components["qcoro-dbus"].names["cmake_find_package"] = "DBus"
            self.cpp_info.components["qcoro-dbus"].names["cmake_find_package_multi"] = "DBus"
        self.cpp_info.components["qcoro-core"].build_modules["cmake_find_package"].append(macros_cmake_path)
        self.cpp_info.components["qcoro-core"].build_modules["cmake_find_package_multi"].append(macros_cmake_path)
