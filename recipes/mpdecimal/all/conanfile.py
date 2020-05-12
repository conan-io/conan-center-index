from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class MpdecimalConan(ConanFile):
    name = "mpdecimal"
    description = "mpdecimal is a package for correctly-rounded arbitrary precision decimal floating point arithmetic."
    license = "BSD-2-Clause"
    topics = ("conan", "mpdecimal", "multiprecision", "library")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.bytereef.org/mpdecimal"
    settings = "os", "compiler", "build_type", "arch"
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

    _autotools = None

    def configure(self):
        if self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("Arch is unsupported")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("mpdecimal-{}".format(self.version), self._source_subfolder)

    _shared_ext_mapping = {
        "Linux": ".so",
        "Windows": ".dll",
        "Macos": ".dylib",
    }

    def _patch_sources(self):
        if self.settings.compiler == "Visual Studio":
            libmpdec_folder = os.path.join(self._source_subfolder, "libmpdec")
            main_version, _ = self.version.split(".", 1)

            makefile_vc_original = os.path.join(libmpdec_folder, "Makefile.vc")
            for msvcrt in ("MDd", "MTd", "MD", "MT"):
                tools.replace_in_file(makefile_vc_original,
                                      msvcrt,
                                      str(self.settings.compiler.runtime))

            tools.replace_in_file(makefile_vc_original,
                                  self.version,
                                  main_version)
        else:
            """
            Using autotools:
            - Build only shared libraries when shared == True
            - Build only static libraries when shared == False
            ! This is more complicated on Windows because when shared=True, an implicit static library has to be built
            """

            shared_ext = self._shared_ext_mapping[str(self.settings.os)]
            static_ext = ".a"
            main_version, _ = self.version.split(".", 1)

            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                                  "libmpdec.a",
                                  "libmpdec{}".format(static_ext))
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                                  "libmpdec.so",
                                  "libmpdec{}".format(shared_ext))

            makefile_in = os.path.join(self._source_subfolder, "Makefile.in")
            mpdec_makefile_in = os.path.join(self._source_subfolder, "libmpdec", "Makefile.in")
            tools.replace_in_file(makefile_in,
                                  "libdir = @libdir@",
                                  "libdir = @libdir@\n"
                                  "bindir = @bindir@")
            if self.options.shared:
                if self.settings.os == "Windows":
                    tools.replace_in_file(makefile_in,
                                          "LIBSHARED = @LIBSHARED@",
                                          "LIBSHARED = libmpdec-{}{}".format(main_version, shared_ext))
                    tools.replace_in_file(makefile_in,
                                          "install: FORCE",
                                          "install: FORCE\n"
                                          "\t$(INSTALL) -d -m 755 $(DESTDIR)$(bindir)")
                    tools.replace_in_file(makefile_in,
                                          "\t$(INSTALL) -m 755 libmpdec/$(LIBSHARED) $(DESTDIR)$(libdir)\n",
                                          "\t$(INSTALL) -m 755 libmpdec/$(LIBSHARED) $(DESTDIR)$(bindir)\n")
                    tools.replace_in_file(makefile_in,
                                          "\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec.so\n",
                                          "")
                else:
                    tools.replace_in_file(makefile_in,
                                          "\t$(INSTALL) -m 644 libmpdec/$(LIBSTATIC) $(DESTDIR)$(libdir)\n",
                                          "")
                    tools.replace_in_file(makefile_in,
                                          "\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec.so",
                                          "\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec{}".format(shared_ext))
            else:
                tools.replace_in_file(makefile_in,
                                      "\t$(INSTALL) -m 755 libmpdec/$(LIBSHARED) $(DESTDIR)$(libdir)\n",
                                      "")
                tools.replace_in_file(makefile_in,
                                      "\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec.so\n",
                                      "")

            tools.replace_in_file(mpdec_makefile_in,
                                  "default: $(LIBSTATIC) $(LIBSHARED)",
                                  "default: $({})".format("LIBSHARED" if self.options.shared else "LIBSTATIC"))

            if self.settings.os == "Windows":
                tools.replace_in_file(mpdec_makefile_in,
                                      "LIBSHARED = @LIBSHARED@",
                                      "LIBSHARED = libmpdec-{}{}".format(main_version, shared_ext))
                tools.replace_in_file(mpdec_makefile_in,
                                      "\tln -sf $(LIBSHARED) libmpdec.so",
                                      "")
                tools.replace_in_file(mpdec_makefile_in,
                                      "\tln -sf $(LIBSHARED) $(LIBSONAME)",
                                      "")
                tools.replace_in_file(mpdec_makefile_in,
                                      "CONFIGURE_LDFLAGS =",
                                      "CONFIGURE_LDFLAGS = -Wl,--out-implib,libmpdec{}".format(static_ext))
            else:
                tools.replace_in_file(mpdec_makefile_in,
                                      "libmpdec.so",
                                      "libmpdec{}".format(shared_ext))

    @property
    def _version_major(self):
        return self.version.split(".", 1)[0]

    def _build_msvc(self):
        libmpdec_folder = os.path.join(self.build_folder, self._source_subfolder, "libmpdec")
        vcbuild_folder = os.path.join(self.build_folder, self._source_subfolder, "vcbuild")
        arch_ext = "{}".format(32 if self.settings.arch == "x86" else 64)
        dist_folder = os.path.join(vcbuild_folder, "dist{}".format(arch_ext))
        os.mkdir(dist_folder)

        shutil.copy(os.path.join(libmpdec_folder, "Makefile.vc"), os.path.join(libmpdec_folder, "Makefile"))
        with tools.chdir(libmpdec_folder):
            with tools.vcvars(self.settings):
                # self.run("nmake /nologo clean")
                self.run("nmake /nologo MACHINE={machine} DLL={dll}".format(
                    machine="ppro" if self.settings.arch == "x86" else "x64",
                    dll="1" if self.options.shared else "0"))

            shutil.copy("mpdecimal.h", dist_folder)
            if self.options.shared:
                shutil.copy("libmpdec-{}.dll".format(self._version_major), os.path.join(dist_folder, "libmpdec-{}.dll".format(self._version_major)))
                shutil.copy("libmpdec-{}.dll.exp".format(self._version_major), os.path.join(dist_folder, "libmpdec-{}.exp".format(self._version_major)))
                shutil.copy("libmpdec-{}.dll.lib".format(self._version_major), os.path.join(dist_folder, "libmpdec-{}.lib".format(self._version_major)))
            else:
                shutil.copy("libmpdec-{}.lib".format(self._version_major), dist_folder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools .configure()
        return self._autotools

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            distfolder = os.path.join(self.build_folder, self._source_subfolder, "vcbuild", "dist{}".format(32 if self.settings.arch == "x86" else 64))
            self.copy("vc*.h", src=os.path.join(self.build_folder, self._source_subfolder, "libmpdec"), dst="include")
            self.copy("*.h", src=distfolder, dst="include")
            self.copy("*.lib", src=distfolder, dst="lib")
            self.copy("*.dll", src=distfolder, dst="bin")
        else:
            with tools.chdir(os.path.join(self.build_folder, self._source_subfolder)):
                autotools = self._configure_autotools()
                autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ["libmpdec-{}".format(self._version_major)]
        else:
            self.cpp_info.libs = ["mpdec"]
        if self.options.shared:
            if self.settings.compiler == "Visual Studio":
                self.cpp_info.defines = ["USE_DLL"]
        else:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["m"]
