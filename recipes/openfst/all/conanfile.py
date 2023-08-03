import os
from itertools import product

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class OpenFstConan(ConanFile):
    name = "openfst"
    description = "A library for constructing, combining, optimizing and searching weighted finite-state-transducers (FSTs)."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openfst.org/twiki/bin/view/FST/WebHome"
    topics = ("asr", "fst", "wfst", "openfst")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_bin": [True, False],
        "enable_compact_fsts": [True, False],
        "enable_compress": [True, False],
        "enable_const_fsts": [True, False],
        "enable_far": [True, False],
        "enable_grm": [True, False],
        "enable_linear_fsts": [True, False],
        "enable_lookahead_fsts": [True, False],
        "enable_mpdt": [True, False],
        "enable_ngram_fsts": [True, False],
        "enable_pdt": [True, False],
        "enable_special": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_bin": True,
        "enable_compact_fsts": False,
        "enable_compress": False,
        "enable_const_fsts": False,
        "enable_far": False,
        "enable_grm": True,
        "enable_linear_fsts": False,
        "enable_lookahead_fsts": False,
        "enable_mpdt": False,
        "enable_ngram_fsts": False,
        "enable_pdt": False,
        "enable_special": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("OpenFst is only supported on linux")

        compilers = {
            "gcc": "8",
            "clang": "7",
        }

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 17)
        minimum_compiler = compilers.get(str(self.settings.compiler))
        if minimum_compiler:
            if Version(self.settings.compiler.version) < minimum_compiler:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires c++17, which your compiler does not support."
                )
        else:
            self.output.warning(
                f"{self.name} requires c++17, but this compiler is unknown to this recipe."
                f" Assuming your compiler supports c++17."
            )

        # Check stdlib ABI compatibility
        if self.settings.compiler == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration(
                f'Using {self.name} with GCC requires "compiler.libcxx=libstdc++11"'
            )
        elif self.settings.compiler == "clang" and self.settings.compiler.libcxx not in ["libstdc++11", "libc++"]:
            raise ConanInvalidConfiguration(
                f'Using {self.name} with Clang requires either "compiler.libcxx=libstdc++11" or "compiler.libcxx=libc++"'
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args += [
            "--enable-bin={}".format(yes_no(self.options.enable_bin)),
            "--enable-compact-fsts={}".format(yes_no(self.options.enable_compact_fsts)),
            "--enable-compress={}".format(yes_no(self.options.enable_compress)),
            "--enable-const-fsts={}".format(yes_no(self.options.enable_const_fsts)),
            "--enable-far={}".format(yes_no(self.options.enable_far)),
            "--enable-grm={}".format(yes_no(self.options.enable_grm)),
            "--enable-linear-fsts={}".format(yes_no(self.options.enable_linear_fsts)),
            "--enable-lookahead-fsts={}".format(yes_no(self.options.enable_lookahead_fsts)),
            "--enable-mpdt={}".format(yes_no(self.options.enable_mpdt)),
            "--enable-ngram-fsts={}".format(yes_no(self.options.enable_ngram_fsts)),
            "--enable-pdt={}".format(yes_no(self.options.enable_pdt)),
            "--enable-special={}".format(yes_no(self.options.enable_special)),
        ]
        tc.extra_cflags.append("-pthread")
        tc.extra_cxxflags.append("-pthread")
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)

        autotools = Autotools(self)
        autotools.install()

        lib_dir = os.path.join(self.package_folder, "lib")
        lib_subdir = os.path.join(self.package_folder, "lib", "fst")
        if os.path.exists(lib_subdir):
            for fn in os.listdir(lib_subdir):
                rename(self,
                       os.path.join(lib_subdir, fn),
                       os.path.join(lib_dir, f"lib{fn}"))
            rmdir(self, lib_subdir)

        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", lib_dir, recursive=True)

    @property
    def _get_const_fsts_libs(self):
        return [f"const{n}-fst" for n in [8, 16, 64]]

    @property
    def _get_compact_fsts_libs(self):
        return [f"compact{n}_{fst}-fst"
                for n, fst in product(
                    [8, 16, 64],
                    ["acceptor", "string", "unweighted_acceptor", "unweighted", "weighted_string"]
                )]

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenFst")
        self.cpp_info.set_property("cmake_target_name", "OpenFst::OpenFst")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.names["cmake_find_package"] = "OpenFst"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenFst"

        self.cpp_info.libs = ["fst"]

        if self.options.enable_compact_fsts:
            self.cpp_info.libs.append("fstcompact")
        if self.options.enable_const_fsts:
            self.cpp_info.libs.append("fstconst")
        if self.options.enable_far or self.options.enable_grm:
            self.cpp_info.libs.append("fstfar")
        if self.options.enable_lookahead_fsts:
            self.cpp_info.libs.append("fstlookahead")
        if self.options.enable_ngram_fsts:
            self.cpp_info.libs.append("fstngram")
        if self.options.enable_special:
            self.cpp_info.libs.append("fstspecial")

        if self.options.enable_bin:
            self.cpp_info.libs.append("fstscript")
            if self.options.enable_compress:
                self.cpp_info.libs.append("fstcompressscript")
            if self.options.enable_compact_fsts:
                self.cpp_info.libs.extend(self._get_compact_fsts_libs)
            if self.options.enable_const_fsts:
                self.cpp_info.libs.extend(self._get_const_fsts_libs)
            if self.options.enable_far or self.options.enable_grm:
                self.cpp_info.libs.append("fstfarscript")
            if self.options.enable_linear_fsts:
                self.cpp_info.libs.append("fstlinearscript")
            if self.options.enable_mpdt or self.options.enable_grm:
                self.cpp_info.libs.append("fstmpdtscript")
            if self.options.enable_pdt or self.options.enable_grm:
                self.cpp_info.libs.append("fstpdtscript")

        self.cpp_info.system_libs = ["pthread", "dl", "m"]

        # TODO: Legacy, to be removed on Conan 2.0
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment var: {bindir}")
        self.env_info.PATH.append(bindir)
