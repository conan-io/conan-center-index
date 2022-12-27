from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, rm, rmdir
from conans import tools, AutoToolsBuildEnvironment
import contextlib
import os

required_conan_version = ">=1.53.0"

class LibxshmfenceConan(ConanFile):
    name = "libxshmfence"
    license = "X11"
    homepage = "https://gitlab.freedesktop.org/xorg/lib/libxshmfence"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Shared memory 'SyncFence' synchronization primitive"
    topics = ("shared", "memory", "syncfence", "synchronization", "interprocess")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # for plain C projects only
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
    
    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported by libxshmfence recipe. Contributions are welcome")

    def build_requirements(self):
        self.build_requires("automake/1.16.5")
        self.build_requires("pkgconf/1.9.3")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def requirements(self):
        self.requires("xorg-proto/2022.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], 
                  destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "{} cl -nologo".format(self._user_info_build["automake"].compile).replace("\\", "/"),
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        self._autotools.libs = []
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        apply_conandata_patches(self)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["xshmfence"]
        self.cpp_info.names["pkg_config"] = "xshmfence"
        self.cpp_info.set_property("pkg_config_name", "xshmfence")
