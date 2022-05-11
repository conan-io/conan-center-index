from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import contextlib
import functools
import os

required_conan_version = ">=1.33.0"


class OpenFstConan(ConanFile):
    name = "openfst"
    description = "A library for constructing, combining, optimizing and searching weighted finite-state-transducers (FSTs)."
    topics = ("asr", "fst", "wfst", "openfst")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.openfst.org/twiki/bin/view/FST/WebHome"
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_bin": [True, False],
        "enable_compact_fsts": [True, False],
        "enable_compress": [True, False],
        "enable_const_fsts": [True, False],
        "enable_far": [True, False],
        "enable_fsts": [True, False],
        "enable_grm": [True, False],
        "enable_linear_fsts": [True, False],
        "enable_lookahead_fsts": [True, False],
        "enable_mpdt": [True, False],
        "enable_ngram_fsts": [True, False],
        "enable_pdt": [True, False],
        "enable_python": [True, False],
        "enable_special": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "enable_bin": True,
        "enable_compact_fsts": False,
        "enable_compress": False,
        "enable_const_fsts": False,
        "enable_far": False,
        "enable_fsts": False,
        "enable_grm": False,
        "enable_linear_fsts": False,
        "enable_lookahead_fsts": False,
        "enable_mpdt": False,
        "enable_ngram_fsts": False,
        "enable_pdt": False,
        "enable_python": False,
        "enable_special": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "OpenFst is supported only on linux")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
    def _build_context(self):
        env = {}
        cc, cxx = self._detect_compilers()
        if not tools.get_env("CC"):
            env["CC"] = cc
        if not tools.get_env("CXX"):
            env["CXX"] = cxx
        with tools.environment_append(env):
            yield

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-bin={}".format(yes_no(self.options.enable_bin)),
            "--enable-compact-fsts={}".format(yes_no(self.options.enable_compact_fsts)),
            "--enable-compress={}".format(yes_no(self.options.enable_compress)),
            "--enable-const-fsts={}".format(yes_no(self.options.enable_const_fsts)),
            "--enable-far={}".format(yes_no(self.options.enable_far)),
            "--enable-fsts={}".format(yes_no(self.options.enable_fsts)),
            "--enable-grm={}".format(yes_no(self.options.enable_grm)),
            "--enable-linear-fsts={}".format(yes_no(self.options.enable_linear_fsts)),
            "--enable-lookahead-fsts={}".format(yes_no(self.options.enable_lookahead_fsts)),
            "--enable-mpdt={}".format(yes_no(self.options.enable_mpdt)),
            "--enable-ngram-fsts={}".format(yes_no(self.options.enable_ngram_fsts)),
            "--enable-pdt={}".format(yes_no(self.options.enable_pdt)),
            "--enable-python={}".format(yes_no(self.options.enable_python)),
            "--enable-special={}".format(yes_no(self.options.enable_special)),
            "LIBS=-lpthread",
        ]
        if tools.get_env("CC"):
            args.append("CC={}".format(tools.get_env("CC")))
        if tools.get_env("CXX"):
            args.append("CXX={}".format(tools.get_env("CXX")))
        autotools.configure(args=args, configure_dir=self._source_subfolder)
        return autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.libs = ["fst"]

        if self.options.enable_bin:
            self.cpp_info.libs.append("fstscript")
            bindir = os.path.join(self.package_folder, "bin")
