import os
import time

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

cspice_license = """THIS SOFTWARE AND ANY RELATED MATERIALS WERE CREATED BY THE
CALIFORNIA INSTITUTE OF TECHNOLOGY (CALTECH) UNDER A U.S.
GOVERNMENT CONTRACT WITH THE NATIONAL AERONAUTICS AND SPACE
ADMINISTRATION (NASA). THE SOFTWARE IS TECHNOLOGY AND SOFTWARE
PUBLICLY AVAILABLE UNDER U.S. EXPORT LAWS AND IS PROVIDED "AS-IS" TO
THE RECIPIENT WITHOUT WARRANTY OF ANY KIND, INCLUDING ANY
WARRANTIES OF PERFORMANCE OR MERCHANTABILITY OR FITNESS FOR A
PARTICULAR USE OR PURPOSE (AS SET FORTH IN UNITED STATES
UCC§2312-§2313) OR FOR ANY PURPOSE WHATSOEVER,
FOR THE SOFTWARE AND RELATED MATERIALS, HOWEVER USED.

IN NO EVENT SHALL CALTECH, ITS JET PROPULSION LABORATORY, OR NASA BE
LIABLE FOR ANY DAMAGES AND/OR COSTS, INCLUDING, BUT NOT LIMITED TO,
INCIDENTAL OR CONSEQUENTIAL DAMAGES OF ANY KIND, INCLUDING
ECONOMIC DAMAGE OR INJURY TO PROPERTY AND LOST PROFITS,
REGARDLESS OF WHETHER CALTECH, JPL, OR NASA BE ADVISED, HAVE
REASON TO KNOW, OR, IN FACT, SHALL KNOW OF THE POSSIBILITY.

RECIPIENT BEARS ALL RISK RELATING TO QUALITY AND PERFORMANCE OF THE
SOFTWARE AND ANY RELATED MATERIALS, AND AGREES TO INDEMNIFY
CALTECH AND NASA FOR ALL THIRD-PARTY CLAIMS RESULTING FROM THE
ACTIONS OF RECIPIENT IN THE USE OF THE SOFTWARE"""

class CspiceConan(ConanFile):
    name = "cspice"
    description = "NASA C SPICE toolkit"
    license = "MIT"
    topics = ("conan", "spice", "naif", "kernels", "space", "nasa", "jpl", "spacecraft", "planet", "robotic")
    homepage = "https://naif.jpl.nasa.gov/naif/toolkit.html"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
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
    def _patch_per_os_arch_compiler(self):
        return {
            "Macos": {
                "x86": {
                    "apple-clang": ["to-MacIntel-OSX.patch", "to-MacIntel-OSX-AppleC-32bit.patch"]
                },
                "x86_64": {
                    "apple-clang": ["to-MacIntel-OSX.patch", "to-MacIntel-OSX-AppleC-64bit.patch"]
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
            "Windows-cygwin": {
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
                    "gcc": ["to-SunSPARC-Solaris.patch", "to-SunSPARC-Solaris-GCC-32bit.patch"],
                    "sun-cc": ["to-SunSPARC-Solaris.patch", "to-SunSPARC-Solaris-SunC-32bit.patch"]
                },
                "sparcv9": {
                    "gcc": ["to-SunSPARC-Solaris.patch", "to-SunSPARC-Solaris-GCC-64bit.patch"],
                    "sun-cc": ["to-SunSPARC-Solaris.patch", "to-SunSPARC-Solaris-SunC-64bit.patch"]
                }
            }
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        os_subsystem = self._get_os_subsystem()
        arch = str(self.settings.arch)
        compiler = str(self.settings.compiler)
        if os_subsystem not in self._patch_per_os_arch_compiler or \
           arch not in self._patch_per_os_arch_compiler[os_subsystem] or \
           compiler not in self._patch_per_os_arch_compiler[os_subsystem][arch]:
            raise ConanInvalidConfiguration("cspice is not compatible with {0} on {1} {2}".format(compiler,
                                                                                                  os_subsystem, arch))

    def _get_os_subsystem(self):
        os_subsystem = str(self.settings.os)
        if self.settings.os == "Windows" and self.settings.os.subsystem != "None":
            os_subsystem += "-" + str(self.settings.os.subsystem)
        return os_subsystem

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
        os_subsystem = self._get_os_subsystem()
        arch = str(self.settings.arch)
        compiler = str(self.settings.compiler)
        for patch_filename in self._patch_per_os_arch_compiler[os_subsystem][arch][compiler]:
            tools.patch(patch_file="patches/{0}/platform/{1}".format(self.version, patch_filename),
                        base_path=self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), cspice_license)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
