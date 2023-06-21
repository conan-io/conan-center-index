import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy

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
        copy(
            self,
            "CMakeLists.txt",
            src=self.recipe_folder,
            dst=os.path.join(self.export_sources_folder, "src"),
        )

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
        # https://github.com/tomojitakasu/RTKLIB/blob/v2.4.3-b34/src/rtklib.h#L6-L15
        defs = {}
        defs["ENAGLO"] = bool(self.options.enable_glonass)
        defs["ENAQZS"] = bool(self.options.enable_qzss)
        defs["ENAGAL"] = bool(self.options.enable_galileo)
        defs["ENACMP"] = bool(self.options.enable_beidou)
        defs["ENAIRN"] = bool(self.options.enable_irnss)
        defs["NFREQ"] = str(self.options.num_frequencies)
        defs["NEXOBS"] = str(self.options.num_ext_obs_codes)
        defs["WIN32"] = self.settings.os == "Windows"
        defs["WIN_DLL"] = self.settings.os == "Windows" and self.options.shared
        return defs

    def generate(self):
        tc = CMakeToolchain(self)
        defs = self._public_defines
        defs["TRACE"] = bool(self.options.trace)
        # TODO: add as options and set libraries correctly
        defs["LAPACK"] = False
        defs["MKL"] = False
        # Set default values
        defs["SVR_REUSEADDR"] = True  # reuse tcp server address
        defs["NOCALLOC"] = False  # use calloc for zero matrix
        defs["CPUTIME_IN_GPST"] = False  # cputime operated in gpst
        defs["RRCENA"] = False  # enable rrc correction
        defs["OUTSTAT_AMB"] = False  # output ambiguity parameters to solution status
        defs["IERS_MODEL"] = False # use IERS tide model
        for k, v in defs.items():
            if v is True:
                tc.preprocessor_definitions[k] = ""
            elif v is not False:
                tc.preprocessor_definitions[k] = v
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE.txt",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["rtklib"]

        for k, v in self._public_defines.items():
            if v is True:
                self.cpp_info.defines.append(k)
            elif v is not False:
                self.cpp_info.defines.append(f"{k}={v}")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("rt")
