from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os
import shutil


class MpdecimalConan(ConanFile):
    name = "mpdecimal"
    version = "2.4.2"
    description = "mpdecimal is a package for correctly-rounded arbitrary precision decimal floating point arithmetic."
    license = "BSD-2-Clause"
    topics = ("mpdecimal", "multiprecision", "library")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.bytereef.org/mpdecimal"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "patches/**"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def configure(self):
        if self._is_msvc and self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("Arch is unsupported")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    _shared_ext_mapping = {
        "Linux": ".so",
        "Windows": ".dll",
        "Macos": ".dylib",
    }

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if not self._is_msvc:
            """
            Using autotools:
            - Build only shared libraries when shared == True
            - Build only static libraries when shared == False
            ! This is more complicated on Windows because when shared=True, an implicit static library has to be built
            """

            shared_ext = self._shared_ext_mapping[str(self.settings.os)]
            static_ext = ".a"
            main_version, _ = self.version.split(".", 1)

            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "configure"),
                                  "libmpdec.a",
                                  "libmpdec{}".format(static_ext))
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "configure"),
                                  "libmpdec.so",
                                  "libmpdec{}".format(shared_ext))

            makefile_in = os.path.join(self._source_subfolder, "Makefile.in")
            mpdec_makefile_in = os.path.join(self._source_subfolder, "libmpdec", "Makefile.in")
            tools.files.replace_in_file(self, makefile_in,
                                  "libdir = @libdir@",
                                  "libdir = @libdir@\n"
                                  "bindir = @bindir@")
            if self.options.shared:
                if self.settings.os == "Windows":
                    tools.files.replace_in_file(self, makefile_in,
                                          "LIBSHARED = @LIBSHARED@",
                                          "LIBSHARED = libmpdec-{}{}".format(main_version, shared_ext))
                    tools.files.replace_in_file(self, makefile_in,
                                          "install: FORCE",
                                          "install: FORCE\n"
                                          "\t$(INSTALL) -d -m 755 $(DESTDIR)$(bindir)")
                    tools.files.replace_in_file(self, makefile_in,
                                          "\t$(INSTALL) -m 755 libmpdec/$(LIBSHARED) $(DESTDIR)$(libdir)\n",
                                          "\t$(INSTALL) -m 755 libmpdec/$(LIBSHARED) $(DESTDIR)$(bindir)\n")
                    tools.files.replace_in_file(self, makefile_in,
                                          "\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec.so\n",
                                          "")
                else:
                    tools.files.replace_in_file(self, makefile_in,
                                          "\t$(INSTALL) -m 644 libmpdec/$(LIBSTATIC) $(DESTDIR)$(libdir)\n",
                                          "")
                    tools.files.replace_in_file(self, makefile_in,
                                          "\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec.so",
                                          "\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec{}".format(shared_ext))
            else:
                tools.files.replace_in_file(self, makefile_in,
                                      "\t$(INSTALL) -m 755 libmpdec/$(LIBSHARED) $(DESTDIR)$(libdir)\n",
                                      "")
                tools.files.replace_in_file(self, makefile_in,
                                      "\tcd $(DESTDIR)$(libdir) && ln -sf $(LIBSHARED) $(LIBSONAME) && ln -sf $(LIBSHARED) libmpdec.so\n",
                                      "")

            tools.files.replace_in_file(self, mpdec_makefile_in,
                                  "default: $(LIBSTATIC) $(LIBSHARED)",
                                  "default: $({})".format("LIBSHARED" if self.options.shared else "LIBSTATIC"))

            if self.settings.os == "Windows":
                tools.files.replace_in_file(self, mpdec_makefile_in,
                                      "LIBSHARED = @LIBSHARED@",
                                      "LIBSHARED = libmpdec-{}{}".format(main_version, shared_ext))
                tools.files.replace_in_file(self, mpdec_makefile_in,
                                      "\tln -sf $(LIBSHARED) libmpdec.so",
                                      "")
                tools.files.replace_in_file(self, mpdec_makefile_in,
                                      "\tln -sf $(LIBSHARED) $(LIBSONAME)",
                                      "")
                tools.files.replace_in_file(self, mpdec_makefile_in,
                                      "CONFIGURE_LDFLAGS =",
                                      "CONFIGURE_LDFLAGS = -Wl,--out-implib,libmpdec{}".format(static_ext))
            else:
                tools.files.replace_in_file(self, mpdec_makefile_in,
                                      "libmpdec.so",
                                      "libmpdec{}".format(shared_ext))

    def _build_msvc(self):
        libmpdec_folder = os.path.join(self.build_folder, self._source_subfolder, "libmpdec")
        vcbuild_folder = os.path.join(self.build_folder, self._source_subfolder, "vcbuild")
        arch_ext = "{}".format(32 if self.settings.arch == "x86" else 64)
        dist_folder = os.path.join(vcbuild_folder, "dist{}".format(arch_ext))
        os.mkdir(dist_folder)

        shutil.copy(os.path.join(libmpdec_folder, "Makefile.vc"), os.path.join(libmpdec_folder, "Makefile"))

        autotools = AutoToolsBuildEnvironment(self)

        with tools.files.chdir(self, libmpdec_folder):
            with tools.vcvars(self.settings):
                self.run("""nmake /nologo MACHINE={machine} DLL={dll} CONAN_CFLAGS="{cflags}" CONAN_LDFLAGS="{ldflags}" """.format(
                    machine="ppro" if self.settings.arch == "x86" else "x64",
                    dll="1" if self.options.shared else "0",
                    cflags=" ".join(autotools.flags),
                    ldflags=" ".join(autotools.link_flags),
                ))

            shutil.copy("mpdecimal.h", dist_folder)
            if self.options.shared:
                shutil.copy("libmpdec-{}.dll".format(self.version), os.path.join(dist_folder, "libmpdec-{}.dll".format(self.version)))
                shutil.copy("libmpdec-{}.dll.exp".format(self.version), os.path.join(dist_folder, "libmpdec-{}.exp".format(self.version)))
                shutil.copy("libmpdec-{}.dll.lib".format(self.version), os.path.join(dist_folder, "libmpdec-{}.lib".format(self.version)))
            else:
                shutil.copy("libmpdec-{}.lib".format(self.version), dist_folder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            self._autotools.link_flags.append("-arch arm64")
        self._autotools .configure()
        return self._autotools

    def build(self):
        self._patch_sources()
        if self._is_msvc:
            self._build_msvc()
        else:
            with tools.files.chdir(self, self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        if self._is_msvc:
            distfolder = os.path.join(self.build_folder, self._source_subfolder, "vcbuild", "dist{}".format(32 if self.settings.arch == "x86" else 64))
            self.copy("vc*.h", src=os.path.join(self.build_folder, self._source_subfolder, "libmpdec"), dst="include")
            self.copy("*.h", src=distfolder, dst="include")
            self.copy("*.lib", src=distfolder, dst="lib")
            self.copy("*.dll", src=distfolder, dst="bin")
        else:
            with tools.files.chdir(self, os.path.join(self.build_folder, self._source_subfolder)):
                autotools = self._configure_autotools()
                autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self._is_msvc:
            self.cpp_info.libs = ["libmpdec-{}".format(self.version)]
        else:
            self.cpp_info.libs = ["mpdec"]
        if self.options.shared:
            if self._is_msvc:
                self.cpp_info.defines = ["USE_DLL"]
        else:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs = ["m"]
