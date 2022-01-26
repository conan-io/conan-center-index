from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import os

required_conan_version = ">=1.33.0"


class LibdeflateConan(ConanFile):
    name = "libdeflate"
    description = "Heavily optimized library for DEFLATE/zlib/gzip compression and decompression."
    license = "MIT"
    topics = ("libdeflate", "compression", "decompression", "deflate", "zlib", "gzip")
    homepage = "https://github.com/ebiggers/libdeflate"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

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

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self._is_msvc and \
           not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _build_msvc(self):
        makefile_msc_file = os.path.join(self._source_subfolder, "Makefile.msc")
        tools.replace_in_file(makefile_msc_file, "CFLAGS = /MD /O2 -I.", "CFLAGS = /nologo $(CFLAGS) -I.")
        tools.replace_in_file(makefile_msc_file, "LDFLAGS =", "")
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    target = "libdeflate.dll" if self.options.shared else "libdeflatestatic.lib"
                    self.run("nmake /f Makefile.msc {}".format(target))

    def _build_make(self):
        makefile = os.path.join(self._source_subfolder, "Makefile")
        tools.replace_in_file(makefile, "-O2", "")
        tools.replace_in_file(
            makefile,
            "-install_name $(SHARED_LIB)",
            "-install_name @rpath/$(SHARED_LIB)", # relocatable shared lib on Macos
        )
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        with tools.chdir(self._source_subfolder):
            autotools.make()

    def build(self):
        if self._is_msvc:
            self._build_msvc()
        else:
            self._build_make()

    def _package_make(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        with tools.chdir(self._source_subfolder):
            autotools.install(args=["PREFIX={}".format(self.package_folder)])
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            suffix = "*static.lib" if self.settings.os == "Windows" else "*.a"
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), suffix)
        else:
            if self.settings.os == "Windows":
                tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.dll")
                suffix = "*deflate.lib"
            elif tools.is_apple_os(self.settings.os):
                suffix = "*.dylib"
            else:
                suffix = "*.so*"
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), suffix)

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        if self._is_msvc:
            self.copy("libdeflate.h", src=self._source_subfolder, dst="include")
            self.copy("*.lib", src=self._source_subfolder, dst="lib")
            self.copy("*.dll", src=self._source_subfolder, dst="bin")
        else:
            self._package_make()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libdeflate")
        prefix = "lib" if self.settings.os == "Windows" else ""
        suffix = "static" if self.settings.os == "Windows" and not self.options.shared else ""
        self.cpp_info.libs = ["{0}deflate{1}".format(prefix, suffix)]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["LIBDEFLATE_DLL"]
