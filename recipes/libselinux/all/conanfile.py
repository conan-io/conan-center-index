from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class LibSELinuxConan(ConanFile):
    name = "libselinux"
    description = "Security-enhanced Linux is a patch of the Linux kernel and a number of utilities with enhanced security functionality designed to add mandatory access controls to Linux"
    topics = ("conan", "selinux", "security-enhanced linux")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SELinuxProject/selinux"
    license = "Unlicense"  # This library (libselinux) is public domain software, i.e. not copyrighted
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    exports_sources = "patches/**"

    def _get_subfolders(self):
        _sepol_subfolder = "libsepol-%s" % self.version
        _selinux_subfolder = "libselinux-%s" % self.version
        return _sepol_subfolder, _selinux_subfolder

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Only Linux is supported")

    def requirements(self):
        self.requires("pcre2/10.36")

    def build_requirements(self):
        self.build_requires("flex/2.6.4")

    def source(self):
        for download in self.conan_data["sources"][self.version]:
            tools.get(**download)

    @property
    def _sepol_soversion(self):
        return "2" if tools.Version(self.version) >= "3.2" else "1"

    @property
    def _selinux_soversion(self):
        return "1"

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        _sepol_subfolder, _selinux_subfolder = self._get_subfolders()
        pcre_inc = os.path.join(self.deps_cpp_info["pcre2"].rootpath,
                                self.deps_cpp_info["pcre2"].includedirs[0])
        pcre_libs = ' '.join(["-l%s" % lib for lib in self.deps_cpp_info["pcre2"].libs])
        sepol_inc = os.path.join(self.source_folder, _sepol_subfolder, "include")
        with tools.chdir(os.path.join(_sepol_subfolder, "src")):
            args = ["libsepol.so.{}".format(self._sepol_soversion) if self.options.shared else "libsepol.a"]
            env_build = AutoToolsBuildEnvironment(self)
            env_build.make(args=args)
        with tools.chdir(os.path.join(_selinux_subfolder, "src")):
            args = ["libselinux.so.{}".format(self._selinux_soversion) if self.options.shared else "libselinux.a",
                    'PCRE_CFLAGS=-DPCRE2_CODE_UNIT_WIDTH=8 -DUSE_PCRE2=1 -I%s -I%s' % (pcre_inc, sepol_inc),
                    'PCRE_LDLIBS=%s' % pcre_libs]
            env_build = AutoToolsBuildEnvironment(self)
            env_build.make(args=args)

    def package(self):
        _sepol_subfolder, _selinux_subfolder = self._get_subfolders()
        self.copy(pattern="LICENSE", dst="licenses", src=_selinux_subfolder)
        for library in [_sepol_subfolder, _selinux_subfolder]:
            self.copy(pattern="*.h", dst="include", src=os.path.join(library, "include"), keep_path=True)
            self.copy(pattern="*.so*", dst="lib", src=library, keep_path=False, symlinks=True)
            self.copy(pattern="*.a", dst="lib", src=library, keep_path=False)

    def package_info(self):
        self.cpp_info.components["selinux"].names["pkg_config"] = "libselinux"
        self.cpp_info.components["selinux"].libs = ["selinux"]
        self.cpp_info.components["selinux"].requires = ["sepol", "pcre2::pcre2"]

        self.cpp_info.components["sepol"].names["pkg_config"] = "libsepol"
        self.cpp_info.components["sepol"].libs = ["sepol"]
