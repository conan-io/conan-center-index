from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, chdir, rm, rmdir
from conans import AutoToolsBuildEnvironment
import functools

required_conan_version = ">=1.52.0"

class libxftConan(ConanFile):
    name = "libxft"
    description = 'X FreeType library'
    topics = ("libxft", "x11", "xorg")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.x.org/wiki/"
    license = "X11"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"
        
    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("xorg/system")
        self.requires("freetype/2.12.1")
        self.requires("fontconfig/2.13.93")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")
        self.build_requires("xorg-macros/1.19.3")
        self.build_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    @functools.lru_cache(1)
    def _configure_autotools(self):
        args = ["--disable-dependency-tracking"]
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])
        autotools = AutoToolsBuildEnvironment(self)
        autotools.configure(args=args, pkg_config_paths=self.build_folder)
        return autotools

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with chdir(self, self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install(args=["-j1"])
        rm(self, "*.la", f"{self.package_folder}/lib", recursive=True)
        rmdir(self, f"{self.package_folder}/lib/pkgconfig")
        rmdir(self, f"{self.package_folder}/share")

    def package_info(self):
        self.cpp_info.names['pkg_config'] = "Xft"
        self.cpp_info.set_property("pkg_config_name", "xft")
        self.cpp_info.libs = ["Xft"]
