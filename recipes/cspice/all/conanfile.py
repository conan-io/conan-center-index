import os
import time

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class CspiceConan(ConanFile):
    name = "cspice"
    description = "NASA C SPICE library"
    license = "TSPA"
    topics = ("conan", "spice", "naif", "kernels", "space", "nasa", "jpl", "spacecraft", "planet", "robotics")
    homepage = "https://naif.jpl.nasa.gov/naif/toolkit.html"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "TSPA.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _patch_per_platform(self):
        return {
            "Macos": {
                "x86": {
                    "apple-clang": ["to-MacIntel-OSX-or-SunSPARC-Solaris.patch", "to-MacIntel-OSX-AppleC-32bit.patch"]
                },
                "x86_64": {
                    "apple-clang": ["to-MacIntel-OSX-or-SunSPARC-Solaris.patch", "to-MacIntel-OSX-AppleC-64bit.patch"]
                }
            },
            "Linux": {
                "x86": {
                    "gcc": ["to-PC-Linux-GCC-32bit.patch"]
                },
                "x86_64": {
                    "gcc": ["to-PC-Linux-GCC-64bit.patch"]
                }
            },
            "Windows": {
                "x86": {
                    "Visual Studio": ["to-PC-Windows.patch", "to-PC-Windows-VisualC-32bit.patch"]
                },
                "x86_64": {
                    "Visual Studio": ["to-PC-Windows.patch", "to-PC-Windows-VisualC-64bit.patch"]
                }
            },
            "cygwin": {
                "x86": {
                    "gcc": []
                },
                "x86_64": {
                    "gcc": ["to-PC-Cygwin-GCC-64bit.patch"]
                }
            },
            "SunOs": {
                "x86": {
                    "sun-cc": ["to-SunIntel-Solaris-SunC-32bit.patch"]
                },
                "x86_64": {
                    "sun-cc": ["to-SunIntel-Solaris-SunC-64bit.patch"]
                },
                "sparc": {
                    "gcc": [
                        "to-MacIntel-OSX-or-SunSPARC-Solaris.patch",
                        "to-SunSPARC-Solaris.patch",
                        "to-SunSPARC-Solaris-GCC-32bit.patch"
                    ],
                    "sun-cc": [
                        "to-MacIntel-OSX-or-SunSPARC-Solaris.patch",
                        "to-SunSPARC-Solaris.patch",
                        "to-SunSPARC-Solaris-SunC-32bit.patch"
                    ]
                },
                "sparcv9": {
                    "gcc": [
                        "to-MacIntel-OSX-or-SunSPARC-Solaris.patch",
                        "to-SunSPARC-Solaris.patch",
                        "to-SunSPARC-Solaris-GCC-64bit.patch"
                    ],
                    "sun-cc": [
                        "to-MacIntel-OSX-or-SunSPARC-Solaris.patch",
                        "to-SunSPARC-Solaris.patch",
                        "to-SunSPARC-Solaris-SunC-64bit.patch"
                    ]
                }
            }
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        os = self._get_os_or_subsystem()
        arch = str(self.settings.arch)
        compiler = str(self.settings.compiler)
        if os not in self._patch_per_platform or \
           arch not in self._patch_per_platform[os] or \
           compiler not in self._patch_per_platform[os][arch]:
            raise ConanInvalidConfiguration("cspice does not support {0} on {1} {2}".format(compiler, os, arch))

    def _get_os_or_subsystem(self):
        if self.settings.os == "Windows" and self.settings.os.subsystem != "None":
            os_or_subsystem = str(self.settings.os.subsystem)
        else:
            os_or_subsystem = str(self.settings.os)
        return os_or_subsystem

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        try:
            os.rename(self.name, self._source_subfolder)
        except:
            # workaround for permission denied on windows
            time.sleep(10)
            os.rename(self.name, self._source_subfolder)

        if "patches" in self.conan_data:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def build(self):
        self._apply_platform_patch()
        cmake = self._configure_cmake()
        cmake.build()

    def _apply_platform_patch(self):
        os = self._get_os_or_subsystem()
        arch = str(self.settings.arch)
        compiler = str(self.settings.compiler)
        for patch_filename in self._patch_per_platform[os][arch][compiler]:
            tools.patch(patch_file="patches/{0}/platform/{1}".format(self.version, patch_filename),
                        base_path=self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def package(self):
        self.copy("TSPA.txt", dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
