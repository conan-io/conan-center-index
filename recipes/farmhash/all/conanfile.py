from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os

required_conan_version = ">=1.33.0"

class farmhashConan(ConanFile):
    name = "farmhash"
    description = "A family of hash functions"
    topics = ("hash", "google", "family")
    license = "MIT"
    homepage = "https://github.com/google/farmhash"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "no_builtin_expect": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "no_builtin_expect": False
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        conf_args = []
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        if self.options.no_builtin_expect:
            self._autotools.defines.append("FARMHASH_NO_BUILTIN_EXPECT")
        self._autotools.configure(configure_dir=self._source_subfolder, args=conf_args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        autotools.install()
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs=["farmhash"]
