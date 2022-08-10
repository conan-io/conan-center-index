from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain

from http.client import HTTPConnection
HTTPConnection.debuglevel = 1


required_conan_version = ">=1.49.0"


class FatFsConan(ConanFile):
    name = "fatfs"
    description = "A generic FAT/exFAT filesystem module for small embedded systems."
    topics = ("filesystem", "embedded")
    license = "BSD-like, see LICENSE.txt"
    homepage = "http://elm-chan.org/fsw/ff/00index_e.html"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "readonly": [True, False],
        "minimize": [0, 1, 2, 3],
        "use_find": [0, 1, 2],
        "use_mkfs": [True, False],
        "use_fastseek": [True, False],
        "use_expand": [True, False],
        "use_chmod": [True, False],
        "use_label": [True, False],
        "use_forward": [True, False],
        "use_strfunc": [0, 1, 2],
        "print_lli": [True, False],
        "print_float": [0, 1, 2],
        "strf_encode": [0, 1, 2, 3],
        "codepage": [0, 437, 720, 737, 771, 775, 850, 852, 855, 857, 860, 861,
                     862, 863, 864, 865, 866, 869, 932, 936, 949, 950],
        "use_lfn": [0, 1, 2, 3],
        "max_lfn": "ANY",
        "lfn_unicode": [0, 1, 2, 3],
        "lfn_buf": "ANY",
        "sfn_buf": "ANY",
        "relative_paths": [0, 1, 2],
        "volumes": [i for i in range(1, 11)],
        "volume_id": [0, 1, 2],
        "volume_strs": "ANY",
        "multi_partition": [True, False],
        "min_ss": "ANY",
        "max_ss": "ANY",
        "lba64": [True, False],
        "min_gpt": "ANY",
        "use_trim": [True, False],
        "tiny": [True, False],
        "exfat": [True, False],
        "nortc": [True, False],
        "nortc_mon": [i for i in range(1, 13)],
        "nortc_mday": [i for i in range(1, 32)],
        "nortc_year": "ANY",
        "nofsinfo": [0, 1, 2, 3],
        "lock": "ANY",
        "reentrant": [True, False],
        "timeout": "ANY"
    }
    default_options = {
        "fPIC": True,
        "readonly": False,
        "minimize": 0,
        "use_find": 0,
        "use_mkfs": False,
        "use_fastseek": False,
        "use_expand": False,
        "use_chmod": False,
        "use_label": False,
        "use_forward": False,
        "use_strfunc": 0,
        "print_lli": False,
        "print_float": 0,
        "strf_encode": 0,
        "codepage": 0,
        "use_lfn": 0,
        "max_lfn": 255,
        "lfn_unicode": 0,
        "lfn_buf": 255,
        "sfn_buf": 12,
        "relative_paths": 0,
        "volumes": 1,
        "volume_id": 0,
        "volume_strs": None,
        "multi_partition": False,
        "min_ss": 512,
        "max_ss": 512,
        "lba64": False,
        "min_gpt": 0x10000000,
        "use_trim": False,
        "tiny": False,
        "exfat": False,
        "nortc": False,
        "nortc_mon": 1,
        "nortc_mday": 1,
        "nortc_year": 2020,
        "nofsinfo": 0,
        "lock": 0,
        "reentrant":  False,
        "timeout": 1000,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.tool_requires("cmake/3.24.0")

    def validate(self):
        if self.options.use_find and self.options.minimize > 2:
            raise ConanInvalidConfiguration(
                "'use_find' option requires 'minimize <= 2'")
        if self.options.use_chmod and self.options.readonly:
            raise ConanInvalidConfiguration(
                "'use_chmod' option requires 'readonly' == False")
        if self.options.exfat and not self.options.use_lfn:
            raise ConanInvalidConfiguration(
                "'exfat' option requires 'use_lfn' == True")

    def export_sources(self):
        self.copy("CMakeLists.txt")
        self.copy("ffconf.h.in")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def source(self):
        files.get(self, **self.conan_data["sources"]
                  [self.version], destination=self._source_subfolder,
                  verify=False)
        files.apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FF_FS_READONLY"] = self.options.readonly
        tc.variables["FF_FS_MINIMIZE"] = self.options.minimize
        tc.variables["FF_USE_FIND"] = self.options.use_find
        tc.variables["FF_USE_MKFS"] = self.options.use_mkfs
        tc.variables["FF_USE_FASTSEEK"] = self.options.use_fastseek
        tc.variables["FF_USE_EXPAND"] = self.options.use_expand
        tc.variables["FF_USE_CHMOD"] = self.options.use_chmod
        tc.variables["FF_USE_LABEL"] = self.options.use_label
        tc.variables["FF_USE_FORWARD"] = self.options.use_forward
        tc.variables["FF_USE_STRFUNC"] = self.options.use_strfunc
        tc.variables["FF_USE_PRINT_LLI"] = self.options.print_lli
        tc.variables["FF_USE_PRINT_FLOAT"] = self.options.print_float
        tc.variables["FF_USE_STRF_ENCODE"] = self.options.strf_encode
        tc.variables["FF_USE_CODE_PAGE"] = self.options.codepage
        tc.variables["FF_USE_LFN"] = self.options.use_lfn
        tc.variables["FF_MAX_LFN"] = self.options.max_lfn
        tc.variables["FF_LFN_UNICODE"] = self.options.lfn_unicode
        tc.variables["FF_LFN_BUF"] = self.options.lfn_buf
        tc.variables["FF_SFN_BUF"] = self.options.sfn_buf
        tc.variables["FF_FS_RPATH"] = self.options.relative_paths
        tc.variables["FF_VOLUMES"] = self.options.volumes
        tc.variables["FF_STR_VOLUME_ID"] = self.options.volume_id
        tc.variables["FF_VOLUME_STRS"] = self.options.volume_strs
        tc.variables["FF_MULTI_PARTITION"] = self.options.multi_partition
        tc.variables["FF_MIN_SS"] = self.options.min_ss
        tc.variables["FF_MAX_SS"] = self.options.max_ss
        tc.variables["FF_LBA64"] = self.options.lba64
        tc.variables["FF_MIN_GPT"] = self.options.min_gpt
        tc.variables["FF_USE_TRIM"] = self.options.use_trim
        tc.variables["FF_FS_TINY"] = self.options.tiny
        tc.variables["FF_FS_EXFAT"] = self.options.exfat
        tc.variables["FF_FS_NORTC"] = self.options.nortc
        tc.variables["FF_NORTC_MON"] = self.options.nortc_mon
        tc.variables["FF_NORTC_MDAY"] = self.options.nortc_mday
        tc.variables["FF_NORTC_YEAR"] = self.options.nortc_year
        tc.variables["FF_FS_NOFSINFO"] = self.options.nofsinfo
        tc.variables["FF_FS_LOCK"] = self.options.lock
        tc.variables["FF_FS_REENTRANT"] = self.options.reentrant
        tc.variables["FF_FS_TIMEOUT"] = self.options.timeout
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = [self.name]
