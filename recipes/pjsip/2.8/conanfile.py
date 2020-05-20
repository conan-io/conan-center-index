import os
import stat
import glob
import shutil
from conans import ConanFile, AutoToolsBuildEnvironment, tools

_openSSL = "openssl"

# based on https://github.com/conan-community/conan-ncurses/blob/stable/6.1/conanfile.py
class PjsipConan(ConanFile):
    name = "pjsip"
    version = "2.8"
    license = "GPL2"
    homepage = "https://github.com/pjsip/pjproject/"
    description = "PJSIP is a free and open source multimedia communication library written in C language implementing standard based protocols such as SIP, SDP, RTP, STUN, TURN, and ICE."
    url = "https://github.com/jens-totemic/conan-pjsip"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "SSL": [True, False],
               # when using little endian on armv7, we can enable neon for pjsip
               # this setting replaces host arm-linux-gnueabihf with armv7l-linux-gnueabihf
               # if our current arch is set to any armv7
               "armv7l": [True, False],
               # the default echo cancellation algo is SPEEX_AEC
               # in order to prefer WEBRTC_AEC, we can disable it
               "disableSpeexAec": [True, False],
               "fPIC": [True, False]}
    # if no OpenSSL is found, pjsip might try to use GnuTLS
    default_options = {"shared": False, "SSL": True, "armv7l": True, "disableSpeexAec":True, "fPIC": True}
    generators = "cmake"
    exports = "LICENSE"
    _autotools = None
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.shared
            del self.default_options["fPIC"]
            del self.default_options["shared"]

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("pjproject-%s" % self.version, self._source_subfolder)
        if not tools.os_info.is_windows:
            configure_file = os.path.join(self._source_subfolder, "configure")
            stc = os.stat(configure_file)
            os.chmod(configure_file, stc.st_mode | stat.S_IEXEC)
            aconfigure_file = os.path.join(self._source_subfolder, "aconfigure")
            stac = os.stat(aconfigure_file)
            os.chmod(aconfigure_file, stac.st_mode | stat.S_IEXEC)

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libalsa/1.1.0")
        if self.options.SSL:
            self.requires(_openSSL+"/1.1.1d")

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            # Getting build errors when cross-compiling webrtc on ARM
            # since we don't use it, just disable it for now
            args = [] # "--disable-libwebrtc"
            if self.settings.os != "Windows" and self.options.shared:
                args.append("--enable-shared")
            if self.options.SSL:
                openSSLroot = self.deps_cpp_info[_openSSL].rootpath
                args.append("--with-ssl=%s" % openSSLroot)
                self.output.info("openSSLroot: %s" % openSSLroot)
            if self.options.disableSpeexAec:
                self._autotools.defines.append("PJMEDIA_HAS_SPEEX_AEC=0")
            # pjsip expects the architecture to be armv7hf-linux-gnueabihf
            host = self._autotools.host
            arch = str(self.settings.arch)

            # turn armv7* into armv7l*
            # autotools checks the architecture by running "config.sub"
            # which does not allow armv7l as architecture unless the manufacturer
            # is set to "unknown"
            if self.options.armv7l and arch.startswith("armv7") and host.startswith("arm-"):
                # a manufacturer entry was already specified
                if host.startswith("arm-unknown-"):
                    host = "armv7l-" + host[:12]
                else:
                    host = "armv7l-unknown-" + host[4:]
                self._autotools.host = host
                self.output.info("Forcing host to: %s" % self._autotools.host)
            #self.output.info(self.deps_cpp_info.lib_paths)
            self.output.info("autotools.library_paths: %s" % self._autotools.library_paths)
            #self.output.info(self.deps_env_info.lib_paths)
            #vars = self._autotools.vars
            #vars["DYLD_LIBRARY_PATH"] = self._autotools.library_paths
            self.output.info("autotools.vars: %s" % self._autotools.vars)

            #with tools.environment_append({"DYLD_LIBRARY_PATH": self._autotools.library_paths}):
            #    self.run("DYLD_LIBRARY_PATH=%s ./configure --enable-shared" % os.environ['DYLD_LIBRARY_PATH'])
            #with tools.environment_append(self._autotools.vars):
            #    self.run("./configure --enable-shared")
            #    self.run("./configure '--enable-shared' '--prefix=/Users/jens/Develop/totemic/conan-pjsip/tmp/source/package' '--bindir=${prefix}/bin' '--sbindir=${prefix}/bin' '--libexecdir=${prefix}/bin' '--libdir=${prefix}/lib' '--includedir=${prefix}/include' '--oldincludedir=${prefix}/include' '--datarootdir=${prefix}/share' --build=x86_64-apple-darwin --host=x86_64-apple-darwin")

            copied_files = []
            # HACK: on OSX, if we compile using shared ssl libraries, a test program
            # compiled by autoconfig does not find the dlyb files in its path, even if
            # we set the DYLD_LIBRARY_PATH correctly, propbably because sub process don't
            # inherit it. To fix it, we simply copy the shared libraries into the build
            # directory and delete them afterwards
            # see also https://stackoverflow.com/questions/33991581/install-name-tool-to-update-a-executable-to-search-for-dylib-in-mac-os-x/33992190#33992190
            for path in self._autotools.library_paths:
                for file in glob.glob(path+"/*.dylib"):
                    filename = file[len(path) + 1:]
                    print(filename)
                    copied_files.append(filename)
                    shutil.copy(file, ".")

            self._autotools.configure(args=args) #, vars=vars

            for copied_file in copied_files:
                os.remove(copied_file)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            env_build_vars = autotools.vars
            # The include paths for dependencies are added to the CPPFLAGS
            # which are not used by pjsip's makefiles. Instead, add them to CFLAGS
            cflags = env_build_vars['CFLAGS'] + " " + env_build_vars['CPPFLAGS']
            env_build_vars['CFLAGS'] = cflags
            self.output.info("env_build_vars: %s" % env_build_vars)
            # only build the lib target, we don't want to build the sample apps
            autotools.make(target="lib", vars=env_build_vars)

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()

    def copy_cleaned(self, source, prefix, dest, excludes):
        for e in source:
            entry = e[len(prefix):] if e.startswith(prefix) else e
            if len(entry) > 0 and not entry in dest and not entry in excludes:
                dest.append(entry)

    def copy_prefix_merged(self, source, prefix, dest):
        cur_prefix = ""
        for e in source:
            if e == prefix:
                cur_prefix = prefix + " "
            else:
                entry = cur_prefix + e
                if len(entry) > 0 and not entry in dest:
                    dest.append(entry)
                cur_prefix = ""

    def package_info(self):
        excluded_dep_libs = []
        for k, v in self.deps_cpp_info.dependencies:
            excluded_dep_libs.extend(v.libs)

        pkgconfigpath = os.path.join(self.package_folder, "lib/pkgconfig")
        self.output.info("package info file: " + pkgconfigpath)
        with tools.environment_append({'PKG_CONFIG_PATH': pkgconfigpath}):
            pkg_config = tools.PkgConfig("libpjproject")
            self.copy_cleaned(pkg_config.libs_only_L, "-L", self.cpp_info.lib_paths, [])
            # exclude all libraries from dependencies here, they are separately included
            self.copy_cleaned(pkg_config.libs_only_l, "-l", self.cpp_info.libs, excluded_dep_libs) #["ssl", "crypto", "z"]
            self.copy_prefix_merged(pkg_config.libs_only_other, "-framework", self.cpp_info.exelinkflags)
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
