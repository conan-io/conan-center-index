from conans import ConanFile, tools, AutoToolsBuildEnvironment
import contextlib
import os

required_conan_version = ">=1.33.0"


class LibebConan(ConanFile):
    name = "libeb"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mistydemeo/eb"
    license = "BSD-3-Clause"
    description = "Libeb is the library for managing EB/EB-G/EB-XA ebooks"
    topics = ("eb", "ebooks", "libeb", "epwing")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_pthread": [True, False],
        "enable_ebnet": [True, False],
        "enable_ipv6": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_pthread": False,
        "enable_ebnet": True,
        "enable_ipv6": True,
    }
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env = {
                    "CC": "cl -nologo",
                    "AR": "lib",
                    "LD": "link -nologo",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("gettext/0.21")
        self.build_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("libiconv/1.17")

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=self._settings_build.os == "Windows")
        self._autotools.libs = []
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) >= "12":
            self._autotools.flags.append("-FS")

        def yes_no(v): return "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-pthread={}".format(yes_no(self.options.enable_pthread)),
            "--enable-ebnet={}".format(yes_no(self.options.enable_ebnet)),
            "--enable-ipv6={}".format(yes_no(self.options.enable_ipv6)),
            "--enable-samples=no",
        ]
        self._autotools.configure(
            args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            tools.rename(os.path.join(self.package_folder, "lib", "eb.dll.lib"),
                         os.path.join(self.package_folder, "lib", "eb.lib"))
        tools.remove_files_by_mask(self.package_folder, "*.la")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))

    def package_info(self):
        if self.settings.os in ("FreeBSD", "Linux", "Macos"):
            self.cpp_info.system_libs = ["m", "resolv"]

        self.cpp_info.names["pkg_config"] = "libeb"
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "libeb")
        self.cpp_info.set_property("cmake_target_name", "libeb::libeb")

        self.cpp_info.names["cmake_find_package"] = "libeb"
        self.cpp_info.names["cmake_find_package_multi"] = "libeb"

        self.cpp_info.libs = ["eb"]

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment var: {}".format(binpath))
        self.env_info.path.append(binpath)
