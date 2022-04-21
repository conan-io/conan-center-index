from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os


required_conan_version = ">=1.43.0"


class BinutilsConan(ConanFile):
    name = "binutils"
    description = "The GNU Binutils are a collection of binary tools."
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://www.gnu.org/software/binutils"
    topics = ("binutils", "ld", "linker", "as", "assembler", "objcopy", "objdump")
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "multilib": [True, False],
        "with_libquadmath": [True, False],
        "target_arch": "ANY",
        "target_os": "ANY"
    }

    default_options = {
        "multilib": True,
        "with_libquadmath": True,
        "target_arch": None,  # Initialized in config_options
        "target_os": None,  # Initialized in config_options
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _settings_target(self):
        return getattr(self, "settings_target", None) or self.settings

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        self.options.target_arch = str(self._settings_target.arch)
        self.options.target_os = str(self._settings_target.os)

    def validate(self):
        if self.settings.compiler in ("msvc", "Visual Studio"):
            raise ConanInvalidConfiguration("This recipe does not support building binutils by this compiler")

        # Check whether the actual target_arch and target_os option are valid (they should be in settings.yml)
        # FIXME: does there exist a stable Conan API to accomplish this?
        if self.options.target_arch not in self.settings.arch.values_range:
            raise ConanInvalidConfiguration(f"target_arch={self.options.target_arch} is invalid (possibilities={self.settings.arch.values_range})")
        if self.options.target_os not in self.settings.os.values_range:
            raise ConanInvalidConfiguration(f"target_os={self.options.target_os} is invalid (possibilities={self.settings.os.values_range})")
        if self._triplet_target is None:
            self._raise_unsupported_configuration("everython", "not ok")

    def package_id(self):
        del self.info.settings.compiler

    def _raise_unsupported_configuration(self, key, value):
        raise ConanInvalidConfiguration(f"This configuration is unsupported by this conan recip. Please consider adding support. ({key}={value})")

    _triplet_arch_lut = {
        "x86": "i686",
        "x86_64": "x86_64",
        "armv8": "aarch64",
    }

    @property
    def _triplet_arch_target(self):
        return self._triplet_arch_lut[str(self.options.target_arch)]

    _triplet_os_lut = {
        "FreeBSD": "freebsd",
        "Linux": "linux",
        "MacOS": "darwin",
        "Windows": "mingw32",
    }

    @property
    def _triplet_os_part(self):
        return self._triplet_os_lut[str(self.options.target_os)]

    _vendor_default = {
        "Windows": "w64",
    }

    @property
    def _triplet_vendor_part(self):
        return self._vendor_default.get(str(self.options.target_os), "cci")

    @property
    def _triplet_target(self):
        return "{}-{}-{}".format(self._triplet_arch_target, self._triplet_vendor_part, self._triplet_os_part)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def requirements(self):
        self.requires("zlib/1.2.12")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    @property
    def _exec_prefix(self):
        return os.path.join(self.package_folder, "bin", "exec_prefix")

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda tf : "yes" if tf else "no"
        conf_args = [
            "--target={}".format(self._triplet_target),
            "--enable-multilib={}".format(yes_no(self.options.multilib)),
            "--with-system-zlib",
            "--disable-nls",
            "exec_prefix={}".format(tools.unix_path(self._exec_prefix)),
        ]
        autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))

        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        target_bindir = os.path.join(self._exec_prefix, self._triplet_target, "bin")
        self.output.info("Appending PATH environment variable: {}".format(target_bindir))
        self.env_info.PATH.append(target_bindir)

        self.user_info.gnu_triplet = self._triplet_target
