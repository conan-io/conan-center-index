import os
from os.path import join

from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import get, rm, copy
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.0"


class QCoroConan(ConanFile):
    name = "qcoro"
    license = "MIT"
    homepage = "https://qcoro.dev/"
    url = "https://github.com/qcoro/qcoro"
    description = "C++ Coroutines for Qt."
    topics = ("coroutines", "qt")
    settings = "os", "compiler", "build_type", "arch"
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
        minimum_versions = {
                "gcc": "10",
                "Visual Studio": "17",
                "msvc": "19.29",
                "clang": "8",
                "apple-clang": "13"
        }
        return minimum_versions

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21.1 <4]")

    def requirements(self):
        self.requires("qt/[>=6.3.1]", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 20)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        #Special check for clang that can only be linked to libc++
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration("imagl requires some C++20 features, which are available in libc++ for clang compiler.")

        compiler_version = str(self.settings.compiler.version)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("qcoro requires C++20. Your compiler is unknown. Assuming it supports C++20.")
        elif lazy_lt_semver(compiler_version, minimum_version):
            raise ConanInvalidConfiguration("qcoro requires some C++20 features, which your {} {} compiler does not support.".format(str(self.settings.compiler), compiler_version))
        else:
            print("Your compiler is {} {} and is compatible.".format(str(self.settings.compiler), compiler_version))

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self.source_folder)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["USE_QT_VERSION"] = "6"
        tc.cache_variables["QCORO_BUILD_EXAMPLES"] = False
        tc.cache_variables["QCORO_ENABLE_ASAN"] = self.options.asan
        tc.cache_variables["BUILD_TESTING"] = False

        # control features
        tc.cache_variables["QCORO_WITH_QTDBUS"] = self.dependencies["qt"].options.with_dbus
        tc.cache_variables["QCORO_WITH_QTWEBSOCKETS"] = self.dependencies["qt"].options.qtwebsockets
        tc.cache_variables["QCORO_WITH_QML"] = bool(self.dependencies["qt"].options.qtdeclarative)
        tc.cache_variables["QCORO_WITH_QTQUICK"] = bool(self.dependencies["qt"].options.qtdeclarative)

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*", join(self.source_folder, "LICENSES"), join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

        for mask in ["Find*.cmake", "*Config*.cmake", "*-config.cmake", "*Targets*.cmake"]:
            rm(self, mask, self.package_folder)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QCoro6")
        self.cpp_info.set_property("pkg_config_name", "qcoro")
        self.cpp_info.set_property('cmake_build_modules', [join("lib", "cmake", "QCoro6Coro", "QCoroMacros.cmake")])

        self.cpp_info.components["core"].set_property("cmake_target_name", "QCoro6::Core")
        self.cpp_info.components["core"].set_property("cmake_target_aliases", ["QCoro::Core"])
        self.cpp_info.components["core"].set_property("pkg_config_name", "qcoro-core")
        self.cpp_info.components["core"].libs = ["QCoro6Core"]
        self.cpp_info.components["core"].includedirs.append(join("include", "qcoro6"))
        self.cpp_info.components["core"].requires = ["qt::qtCore"]
        self.cpp_info.components["core"].builddirs.append(join("lib", "cmake", "QCoro6Coro"))

        self.cpp_info.components["network"].set_property("cmake_target_name", "QCoro6::Network")
        self.cpp_info.components["network"].set_property("cmake_target_aliases", ["QCoro::Network"])
        self.cpp_info.components["network"].set_property("pkg_config_name", "qcoro-network")
        self.cpp_info.components["network"].libs = ["QCoro6Network"]
        self.cpp_info.components["network"].requires = ["qt::qtNetwork"]

        if self.dependencies["qt"].options.with_dbus:
            self.cpp_info.components["dbus"].set_property("cmake_target_name", "QCoro6::DBus")
            self.cpp_info.components["dbus"].set_property("cmake_target_aliases", ["QCoro::DBus"])
            self.cpp_info.components["dbus"].set_property("pkg_config_name", "qcoro-dbus")
            self.cpp_info.components["dbus"].libs = ["QCoroDBus"]
            self.cpp_info.components["core"].requires = ["qt::qtDBus"]
