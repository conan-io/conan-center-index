from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class CorradeConan(ConanFile):
    name = "corrade"
    description = "Corrade is a multiplatform utility library written in C++11/C++14."
    topics = ("conan", "corrade", "magnum", "filesystem", "console", "environment", "os")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics/corrade"
    license = "MIT"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    short_paths = True
    _cmake = None

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_deprecated": [True, False],
        "with_interconnect": [True, False],
        "with_main": [True, False],
        "with_pluginmanager": [True, False],
        "with_testsuite": [True, False],
        "with_utility": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_deprecated": True,
        "with_interconnect": True,
        "with_main": True,
        "with_pluginmanager": True,
        "with_testsuite": True,
        "with_utility": True,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < 14:
            raise ConanInvalidConfiguration("Corrade requires Visual Studio version 14 or greater")
        if tools.cross_building(self):
            self.output.warn("This Corrade recipe could not be prepared for cross building")
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
            self._cmake.definitions["BUILD_DEPRECARED"] = self.options["build_deprecated"]
            self._cmake.definitions["WITH_INTERCONNECT"] = self.options["with_interconnect"]
            self._cmake.definitions["WITH_MAIN"] = self.options["with_main"]
            self._cmake.definitions["WITH_PLUGINMANAGER"] = self.options["with_pluginmanager"]
            self._cmake.definitions["WITH_TESTSUITE"] = self.options["with_testsuite"]
            self._cmake.definitions["WITH_UTILITY"] = self.options["with_utility"]
            self._cmake.definitions["WITH_RC"] = "ON"

            # Corrade uses suffix on the resulting "lib"-folder when running cmake.install()
            # Set it explicitly to empty, else Corrade might set it implicitly (eg. to "64")
            self._cmake.definitions["LIB_SUFFIX"] = ""

            if self.settings.compiler == "Visual Studio":
                self._cmake.definitions["CORRADE_MSVC2015_COMPATIBILITY"] = "ON" if self.settings.compiler.version == "14" else "OFF"
                self._cmake.definitions["CORRADE_MSVC2017_COMPATIBILITY"] = "ON" if self.settings.compiler.version == "15" else "OFF"
                self._cmake.definitions["CORRADE_MSVC2019_COMPATIBILITY"] = "ON" if self.settings.compiler.version == "16" else "OFF"

            self._cmake.configure(build_folder=self._build_subfolder)

        return self._cmake


    def build_requirements(self):
        if hasattr(self, 'settings_build') and tools.cross_building(self.settings, skip_x64_x86=True):
            self.build_requires("corrade/{}".format(self.version))

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        share_cmake = os.path.join(self.package_folder, "share", "cmake", "Corrade")
        self.copy("UseCorrade.cmake", src=share_cmake, dst=os.path.join(self.package_folder, "lib", "cmake", "Corrade"))
        self.copy("CorradeLibSuffix.cmake", src=share_cmake, dst=os.path.join(self.package_folder, "lib", "cmake", "Corrade"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def _sort_libs(self, correct_order, libs, lib_suffix="", reverse_result=False):
        # Add suffix for correct string matching
        correct_order[:] = [s.__add__(lib_suffix) for s in correct_order]

        result = []
        for expectedLib in correct_order:
            for lib in libs:
                if expectedLib == lib:
                    result.append(lib)

        if reverse_result:
            # Linking happens in reversed order
            result.reverse()
        return result

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Corrade"
        self.cpp_info.names["cmake_find_package_multi"] = "Corrade"

        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.build_modules.append(os.path.join("lib", "cmake", "Corrade", "UseCorrade.cmake"))
        self.cpp_info.build_modules.append(os.path.join("lib", "cmake", "Corrade", "CorradeLibSuffix.cmake"))

        # See dependency order here: https://doc.magnum.graphics/magnum/custom-buildsystems.html
        allLibs = [
            #1
            "CorradeMain",
            "CorradeUtility",
            "CorradeContainers",
            #2
            "CorradeInterconnect",
            "CorradePluginManager",
            "CorradeTestSuite",
        ]

        # Sort all built libs according to above, and reverse result for correct link order
        suffix = "-d" if self.settings.build_type == "Debug" else ""
        builtLibs = tools.collect_libs(self)
        self.cpp_info.libs = self._sort_libs(allLibs, builtLibs, suffix, True)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "dl"]

        self.cpp_info.builddirs = [os.path.join(self.package_folder, "lib", "cmake", "Corrade")]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
