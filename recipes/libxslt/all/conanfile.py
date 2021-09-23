import glob
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment


class LibxsltConan(ConanFile):
    name = "libxslt"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libxslt is a software library implementing XSLT processor, based on libxml2"
    topics = ("XSLT", "processor")
    homepage = "https://xmlsoft.org"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    default_options = {'shared': False,
                       'fPIC': True,
                       "debugger": False,
                       "crypto": False,
                       "profiler": False,
                       "plugins": False}
    options = {name: [True, False] for name in default_options.keys()}
    _option_names = [name for name in default_options.keys() if name not in ["shared", "fPIC"]]
    _source_subfolder = "source_subfolder"
    exports_sources = "patches/**"

    def requirements(self):
        self.requires("libxml2/2.9.12")

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    @property
    def _full_source_subfolder(self):
        return os.path.join(self.source_folder, self._source_subfolder)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libxslt-{0}".format(self.version), self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        if self._is_msvc:
            self._build_windows()
        else:
            self._build_with_configure()

    def _build_windows(self):
        with tools.chdir(os.path.join(self._full_source_subfolder, 'win32')):
            debug = "yes" if self.settings.build_type == "Debug" else "no"
            static = "no" if self.options.shared else "yes"

            with tools.vcvars(self.settings):
                args = ["cscript",
                        "configure.js",
                        "compiler=msvc",
                        "prefix=%s" % self.package_folder,
                        "cruntime=/%s" % self.settings.compiler.runtime,
                        "debug=%s" % debug,
                        "static=%s" % static,
                        'include="%s"' % ";".join(self.deps_cpp_info.include_paths),
                        'lib="%s"' % ";".join(self.deps_cpp_info.lib_paths),
                        'iconv=no',
                        'xslt_debug=no']
                for name in self._option_names:
                    cname = {"plugins": "modules"}.get(name, name)
                    value = getattr(self.options, name)
                    value = "yes" if value else "no"
                    args.append("%s=%s" % (cname, value))
                configure_command = ' '.join(args)
                self.output.info(configure_command)
                self.run(configure_command)

                # Fix library names because they can be not just zlib.lib
                def format_libs(package):
                    libs = []
                    for lib in self.deps_cpp_info[package].libs:
                        libname = lib
                        if not libname.endswith('.lib'):
                            libname += '.lib'
                        libs.append(libname)
                    for lib in self.deps_cpp_info[package].system_libs:
                        libname = lib
                        if not libname.endswith('.lib'):
                            libname += '.lib'
                        libs.append(libname)
                    return ' '.join(libs)

                def fix_library(option, package, old_libname):
                    if option:
                        tools.replace_in_file("Makefile.msvc",
                                              "LIBS = %s" % old_libname,
                                              "LIBS = %s" % format_libs(package))

                if "icu" in self.deps_cpp_info.deps:
                    fix_library(True, 'icu', 'wsock32.lib')

                tools.replace_in_file("Makefile.msvc", "libxml2.lib", format_libs("libxml2"))
                tools.replace_in_file("Makefile.msvc", "libxml2_a.lib", format_libs("libxml2"))

                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    self.run("nmake /f Makefile.msvc install")

    def _build_with_configure(self):
        env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        full_install_subfolder = tools.unix_path(self.package_folder)
        # fix rpath
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._full_source_subfolder, "configure"), r"-install_name \$rpath/", "-install_name ")
        configure_args = ['--with-python=no', '--prefix=%s' % full_install_subfolder]
        if self.options.shared:
            configure_args.extend(['--enable-shared', '--disable-static'])
        else:
            configure_args.extend(['--enable-static', '--disable-shared'])

        libxml_src = "--with-libxml-src=" + tools.unix_path(self.deps_cpp_info["libxml2"].rootpath)
        configure_args.append(libxml_src)

        for name in self._option_names:
            value = getattr(self.options, name)
            value = ("--with-%s" % name) if value else ("--without-%s" % name)
            configure_args.append(value)

        env_build.configure(args=configure_args, configure_dir=self._full_source_subfolder)
        env_build.make(args=["install", "V=1"])

    def package(self):
        self.copy("COPYING", src=self._full_source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.settings.os == "Windows":
            # There is no way to avoid building the tests, but at least we don't want them in the package
            for prefix in ["run", "test"]:
                for test in glob.glob("%s/bin/%s*" % (self.package_folder, prefix)):
                    os.remove(test)
        if self.settings.compiler == "Visual Studio":
            if self.settings.build_type == "Debug":
                os.unlink(os.path.join(self.package_folder, "bin", "libexslt.pdb"))
                os.unlink(os.path.join(self.package_folder, "bin", "libxslt.pdb"))
                os.unlink(os.path.join(self.package_folder, "bin", "xsltproc.pdb"))
            if self.options.shared:
                os.unlink(os.path.join(self.package_folder, "lib", "libxslt_a.lib"))
                os.unlink(os.path.join(self.package_folder, "lib", "libexslt_a.lib"))
            else:
                os.unlink(os.path.join(self.package_folder, "lib", "libxslt.lib"))
                os.unlink(os.path.join(self.package_folder, "lib", "libexslt.lib"))
                os.unlink(os.path.join(self.package_folder, "bin", "libxslt.dll"))
                os.unlink(os.path.join(self.package_folder, "bin", "libexslt.dll"))
        for f in "libxslt.la", "libexslt.la":
            la = os.path.join(self.package_folder, 'lib', f)
            if os.path.isfile(la):
                os.unlink(la)

    def package_info(self):
        self.cpp_info.libs = ['exslt', 'xslt']
        if self._is_msvc:
            if self.options.shared:
                self.cpp_info.libs = ['lib%s' % l for l in self.cpp_info.libs]
            else:
                self.cpp_info.libs = ['lib%s_a' % l for l in self.cpp_info.libs]
        self.cpp_info.includedirs.append(os.path.join("include", "libxslt"))
        if not self.options.shared:
            self.cpp_info.defines = ["LIBXSLT_STATIC"]
        if self.settings.os in ["Linux", "Macos", "FreeBSD", "Android"]:
            self.cpp_info.system_libs.append('m')
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append('ws2_32')
