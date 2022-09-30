from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class QCoroConan(ConanFile):
    name = "qcoro"
    license = "MIT"
    homepage = "https://github.com/danvratil/qcoro"
    url = "https://github.com/conan-io/conan-center-index"
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
    generators = "cmake", "cmake_find_package_multi"
    exports_sources = ["CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        self.build_requires("cmake/3.23.2")

    def requirements(self):
        self.requires("qt/6.3.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 20)

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
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)

        self._cmake.definitions["QCORO_BUILD_EXAMPLES"] = False
        self._cmake.definitions["QCORO_ENABLE_ASAN"] = self.options.asan
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["QCORO_WITH_QTDBUS"] = self.options["qt"].with_dbus
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("*", dst="licenses", src=os.path.join(self._source_subfolder, "LICENSES"))
        cmake = self._configure_cmake()
        cmake.install()

        for mask in ["Find*.cmake", "*Config*.cmake", "*-config.cmake", "*Targets*.cmake"]:
            tools.remove_files_by_mask(self.package_folder, mask)

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "QCoro6"
        self.cpp_info.filenames["cmake_find_package_multi"] = "QCoro6"
        self.cpp_info.set_property("cmake_file_name", "QCoro6")
        self.cpp_info.names["cmake_find_package"] = "QCoro"
        self.cpp_info.names["cmake_find_package_multi"] = "QCoro"

        self.cpp_info.components["qcoro-core"].set_property("cmake_target_name", "QCoro::Core")
        self.cpp_info.components["qcoro-core"].names["cmake_find_package"] = "Core"
        self.cpp_info.components["qcoro-core"].names["cmake_find_package_multi"] = "Core"
        self.cpp_info.components["qcoro-core"].libs = ["QCoro6Core"]
        self.cpp_info.components["qcoro-core"].includedirs.append(os.path.join("include", "qcoro6", "qcoro"))
        self.cpp_info.components["qcoro-core"].requires = ["qt::qtCore"]
        self.cpp_info.components["qcoro-core"].build_modules["cmake_find_package"].append(os.path.join("lib", "cmake", "QCoro6Coro", "QCoroMacros.cmake"))
        self.cpp_info.components["qcoro-core"].build_modules["cmake_find_package_multi"].append(os.path.join("lib", "cmake", "QCoro6Coro", "QCoroMacros.cmake"))
        self.cpp_info.components["qcoro-core"].builddirs.append(os.path.join("lib", "cmake", "QCoro6Coro"))

        self.cpp_info.components["qcoro-network"].set_property("cmake_target_name", "QCoro::Network")
        self.cpp_info.components["qcoro-network"].names["cmake_find_package"] = "Network"
        self.cpp_info.components["qcoro-network"].names["cmake_find_package_multi"] = "Network"
        self.cpp_info.components["qcoro-network"].libs = ["QCoro6Network"]
        self.cpp_info.components["qcoro-network"].requires = ["qt::qtNetwork"]

        if self.options["qt"].with_dbus:
            self.cpp_info.components["qcoro-dbus"].set_property("cmake_target_name", "QCoro::DBus")
            self.cpp_info.components["qcoro-dbus"].names["cmake_find_package"] = "DBus"
            self.cpp_info.components["qcoro-dbus"].names["cmake_find_package_multi"] = "DBus"
            self.cpp_info.components["qcoro-dbus"].libs = ["QCoroDBus"]
            self.cpp_info.components["qcoro-core"].requires = ["qt::qtDBus"]
