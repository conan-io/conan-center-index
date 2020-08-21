from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools
from conans.errors import ConanException
from contextlib import contextmanager
import os
import re
import shlex


class LibUSBCompatConan(ConanFile):
    name = "libusb-compat"
    description = "A compatibility layer allowing applications written for libusb-0.1 to work with libusb-1.0"
    license = ("LGPL-2.1", "BSD-3-Clause")
    homepage = "https://github.com/libusb/libusb-compat-0.1"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "patches/**", "CMakeLists.txt.in"
    topics = ("conan", "libusb", "compatibility", "usb")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_logging": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_logging": False,
    }
    generators = "cmake", "pkg_config"

    _autotools = None
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libusb-compat-{}".format(self.version), self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("libusb/1.0.23")
        if self.settings.compiler == "Visual Studio":
            self.requires("dirent/1.23.2")

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        self.build_requires("pkgconf/1.7.3")
        if tools.os_info.is_windows and not os.environ.get("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def _iterate_lib_paths_win(self, lib):
        """Return all possible library paths for lib"""
        for lib_path in self.deps_cpp_info.lib_paths:
            for prefix in "", "lib":
                for suffix in "", ".a", ".dll.a", ".lib", ".dll.lib":
                    fn = os.path.join(lib_path, "{}{}{}".format(prefix, lib, suffix))
                    if not fn.endswith(".a") and not fn.endswith(".lib"):
                        continue
                    yield fn

    @property
    def _absolute_dep_libs_win(self):
        absolute_libs = []
        for lib in self.deps_cpp_info.libs:
            for fn in self._iterate_lib_paths_win(lib):
                if not os.path.isfile(fn):
                    continue
                absolute_libs.append(fn)
                break
        return absolute_libs

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(source_dir=os.path.join(self._source_subfolder, "libusb"))
        return self._cmake

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.compiler == "Visual Studio":
            # Use absolute paths of the libraries instead of the library names only.
            # Otherwise, the configure script will say that the compiler not working
            # (because it interprets the libs as input source files)
            self._autotools.libs = list(tools.unix_path(l) for l in self._absolute_dep_libs_win) + self.deps_cpp_info.system_libs
        conf_args = [
            "--disable-examples-build",
            "--enable-log" if self.options.enable_logging else "--disable-log",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        pkg_config_paths = [tools.unix_path(os.path.abspath(self.install_folder))]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder, pkg_config_paths=pkg_config_paths)
        return self._autotools

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env = {
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "LD": "link -nologo",
                    "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
                    "DLLTOOL": ":",
                    "OBJDUMP": ":",
                    "RANLIB": ":",
                    "STRIP": ":",
                }
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _extract_makefile_variable(self, makefile, variable):
        makefile_contents = tools.load(makefile)
        match = re.search("{}[ \t]*=[ \t]*((?:(?:[a-zA-Z0-9 \t.=/_-])|(?:\\\\\"))*(?:\\\\\n(?:(?:[a-zA-Z0-9 \t.=/_-])|(?:\\\"))*)*)\n".format(variable), makefile_contents)
        if not match:
            raise ConanException("Cannot extract variable {} from {}".format(variable, makefile_contents))
        lines = [line.strip(" \t\\") for line in match.group(1).split()]
        return [item for line in lines for item in shlex.split(line) if item]

    def _extract_autotools_variables(self):
        makefile = os.path.join(self._source_subfolder, "libusb", "Makefile.am")
        sources = self._extract_makefile_variable(makefile, "libusb_la_SOURCES")
        headers = self._extract_makefile_variable(makefile, "include_HEADERS")
        return sources, headers

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.settings.os == "Windows":
            api = "__declspec(dllexport)" if self.options.shared else ""
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure.ac"),
                                  "\nAC_DEFINE([API_EXPORTED]",
                                  "\nAC_DEFINE([API_EXPORTED], [{}], [API])\n#".format(api))
            # libtool disallows building shared libraries that link to static libraries
            # This will override this and add the dependency
            tools.replace_in_file(os.path.join(self._source_subfolder, "ltmain.sh"),
                                  "droppeddeps=yes", "droppeddeps=no && func_append newdeplibs \" $a_deplib\"")

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
        if self.settings.os == "Windows":
            cmakelists_in = tools.load("CMakeLists.txt.in")
            sources, headers = self._extract_autotools_variables()
            tools.save(os.path.join(self._source_subfolder, "libusb", "CMakeLists.txt"), cmakelists_in.format(
                libusb_sources=" ".join(sources),
                libusb_headers=" ".join(headers),
            ))
            tools.replace_in_file("config.h", "\n#define API_EXPORTED", "\n#define API_EXPORTED //")
            cmake = self._configure_cmake()
            cmake.build()
        else:
            with self._build_context():
                autotools.make()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if self.settings.os == "Windows":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            with self._build_context():
                autotools = self._configure_autotools()
                autotools.install()

            os.unlink(os.path.join(self.package_folder, "bin", "libusb-config"))
            os.unlink(os.path.join(self.package_folder, "lib", "libusb.la"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libusb"
        self.cpp_info.libs = ["usb"]
        if not self.options.shared:
            self.cpp_info.defines = ["LIBUSB_COMPAT_STATIC"]
