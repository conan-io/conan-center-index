import glob
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment


class LibxsltConan(ConanFile):
    name = "libxslt"
    version = "1.1.33"
    url = "https://github.com/bincrafters/conan-libxslt"
    description = "libxslt is a software library implementing XSLT processor, based on libxml2"
    topics = ("XSLT", "processor")
    homepage = "https://xmlsoft.org"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {'shared': False,
                       'fPIC': True}
    exports_sources = ["FindLibXml2.cmake"]
    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires("libxml2/2.9.9")

    @property
    def _is_msvc(self):
        return self.settings.compiler == 'Visual Studio'

    @property
    def _full_source_subfolder(self):
        return os.path.join(self.source_folder, self._source_subfolder)

    def source(self):
        tools.get("http://xmlsoft.org/sources/libxslt-{0}.tar.gz".format(self.version),
                  sha256="8e36605144409df979cab43d835002f63988f3dc94d5d3537c12796db90e38c8")
        os.rename("libxslt-{0}".format(self.version), self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build(self):
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
                        'xslt_debug=no',
                        'debugger=no',
                        'crypto=no']
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
        in_win = self.settings.os == "Windows"
        env_build = AutoToolsBuildEnvironment(self, win_bash=in_win)
        if not in_win:
            env_build.fpic = self.options.fPIC
        full_install_subfolder = tools.unix_path(self.package_folder) if in_win else self.package_folder
        # fix rpath
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._full_source_subfolder, "configure"), r"-install_name \$rpath/", "-install_name ")
        configure_args = ['--with-python=no', '--prefix=%s' % full_install_subfolder]
        if env_build.fpic:
            configure_args.extend(['--with-pic'])
        if self.options.shared:
            configure_args.extend(['--enable-shared', '--disable-static'])
        else:
            configure_args.extend(['--enable-static', '--disable-shared'])

        xml_config = tools.unix_path(self.deps_cpp_info["libxml2"].rootpath) + "/bin/xml2-config"

        configure_args.extend([
            '--without-crypto',
            '--without-debugger',
            '--without-plugins',
            'XML_CONFIG=%s' % xml_config
        ])

        # Disable --build when building for iPhoneSimulator. The configure script halts on
        # not knowing if it should cross-compile.
        build = None
        if self.settings.os == "iOS" and self.settings.arch == "x86_64":
            build = False

        env_build.configure(args=configure_args, build=build, configure_dir=self._full_source_subfolder)
        env_build.make(args=["install", "V=1"])

    def package(self):
        # copy package license
        self.copy("COPYING", src=self._full_source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
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
        la = os.path.join(self.package_folder, 'lib', 'libxslt.la')
        if os.path.isfile(la):
            os.unlink(la)

    def package_info(self):
        if self._is_msvc:
            self.cpp_info.libs = ['libxslt' if self.options.shared else 'libxslt_a']
        else:
            self.cpp_info.libs = ['xslt']
        self.cpp_info.includedirs.append(os.path.join("include", "libxslt"))
        if self.settings.os == "Linux" or self.settings.os == "Macos":
            self.cpp_info.libs.append('m')
        if self.settings.os == "Windows":
            self.cpp_info.libs.append('ws2_32')
