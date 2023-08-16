import os

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, export_conandata_patches, apply_conandata_patches

required_conan_version = ">=1.53.0"


class RtklibConan(ConanFile):
    name = "rtklib"
    description = "Library for standard and precise positioning with GNSS"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tomojitakasu/RTKLIB"
    topics = ("gnss", "rtk", "ppp", "rinex", "rtcm", "ublox", "novatel", "septentrio")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "trace": [True, False],
        "enable_glonass": [True, False],
        "enable_qzss": [True, False],
        "enable_galileo": [True, False],
        "enable_beidou": [True, False],
        "enable_irnss": [True, False],
        "num_frequencies": ["ANY"],
        "num_ext_obs_codes": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "trace": False,
        "enable_glonass": True,
        "enable_qzss": True,
        "enable_galileo": True,
        "enable_beidou": True,
        "enable_irnss": True,
        "num_frequencies": 5,
        "num_ext_obs_codes": 3,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt",
             src=self.recipe_folder,
             dst=os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _public_defines(self):
        # Values used in the public header
        # https://github.com/tomojitakasu/RTKLIB/blob/v2.4.3-b34/src/rtklib.h#L6-L15
        # Default values are based on
        # https://github.com/tomojitakasu/RTKLIB/blob/v2.4.3-b34/app/consapp/rnx2rtkp/gcc/makefile#L5
        # https://github.com/tomojitakasu/RTKLIB/blob/v2.4.3-b34/app/consapp/convbin/gcc/makefile#L10
        defs = {}
        defs["ENAGLO"] = self.options.enable_glonass
        defs["ENAQZS"] = self.options.enable_qzss
        defs["ENAGAL"] = self.options.enable_galileo
        defs["ENACMP"] = self.options.enable_beidou
        defs["ENAIRN"] = self.options.enable_irnss
        defs["NFREQ"] = str(self.options.num_frequencies)
        defs["NEXOBS"] = str(self.options.num_ext_obs_codes)
        defs["WIN32"] = self.settings.os == "Windows"
        defs["WIN_DLL"] = self.settings.os == "Windows" and self.options.shared
        return defs

    def generate(self):
        tc = CMakeToolchain(self)
        defs = self._public_defines
        defs["TRACE"] = self.options.trace
        # TODO: add as options and set libraries correctly
        defs["LAPACK"] = False
        defs["MKL"] = False
        # Set default values
        defs["SVR_REUSEADDR"] = True  # reuse tcp server address
        defs["NOCALLOC"] = False  # use calloc for zero matrix
        defs["CPUTIME_IN_GPST"] = False  # cputime operated in gpst
        defs["RRCENA"] = False  # enable rrc correction
        defs["OUTSTAT_AMB"] = False  # output ambiguity parameters to solution status
        defs["IERS_MODEL"] = False  # use IERS tide model
        if is_apple_os(self):
            # Add baud rates missing from termios.h for stream.c
            defs["B460800"] = 460800
            defs["B921600"] = 921600
        for k, v in defs.items():
            if type(v) in (str, int):
                tc.preprocessor_definitions[k] = v
            elif v:
                tc.preprocessor_definitions[k] = ""
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["rtklib"]

        for k, v in self._public_defines.items():
            if type(v) in (str, int):
                self.cpp_info.defines.append(f"{k}={v}")
            elif v:
                self.cpp_info.defines.append(k)

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "winmm"]
