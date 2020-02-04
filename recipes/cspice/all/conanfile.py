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
    exports_sources = ["CMakeLists.txt", "patches/**"]
    exports = ["TSPA.txt"]
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
    def _patches_per_triplet(self):
        """List of patches per triplet, in order to retrieve CSpice source code
        of the triplet from CSpice source code of Cygwin GCC 32bit triplet.
        """
        # These patches were created by comparing the source code of each CSpice
        # package (one per supported triplet) with CSpice's source code of
        # Cygwin GCC 32bit package. All packages can be found at
        # https://naif.jpl.nasa.gov/pub/naif/misc/toolkits_N${version}/C.
        # By CSpice's source code, we mean .h and .c files under "include" and
        # "src/cspice" directories. Others files are not relevant for this
        # conan recipe.
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

        self._raise_if_not_supported_triplet()

    def _raise_if_not_supported_triplet(self):
        os = self._get_os_or_subsystem()
        arch = str(self.settings.arch)
        compiler = str(self.settings.compiler)
        if os not in self._patches_per_triplet:
            raise ConanInvalidConfiguration("cspice does not support {0}".format(os))
        if arch not in self._patches_per_triplet[os]:
            raise ConanInvalidConfiguration("cspice does not support {0} {1}".format(os, arch))
        if compiler not in self._patches_per_triplet[os][arch]:
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

    def build(self):
        self._apply_global_patches()
        self._apply_triplet_patches()
        cmake = self._configure_cmake()
        cmake.build()

    def _apply_global_patches(self):
        if "patches" in self.conan_data:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def _apply_triplet_patches(self):
        os = self._get_os_or_subsystem()
        arch = str(self.settings.arch)
        compiler = str(self.settings.compiler)
        for patch_filename in self._patches_per_triplet[os][arch][compiler]:
            tools.patch(patch_file="patches/{0}/triplets/{1}".format(self.version, patch_filename),
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
