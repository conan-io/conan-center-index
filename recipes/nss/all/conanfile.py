from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import msvc_runtime_flag
import os, glob


class NSSConan(ConanFile):
    name = "nss"
    license = "MPL-2.0"
    homepage = "https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Network Security Services"
    topics = ("network", "security", "crypto", "ssl")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.compiler == "Visual Studio" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.os == "Windows":
            self.build_requires("mozilla-build/3.3")
        if hasattr(self, "settings_build"):
            self.build_requires("sqlite3/3.38.1")

    def configure(self):
        self.options["nspr"].shared = True
        self.options["sqlite3"].shared = True

        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("nspr/4.33")
        self.requires("sqlite3/3.38.1")
        self.requires("zlib/1.2.12")

    def validate(self):
        if not self.options.shared:
            raise ConanInvalidConfiguration("NSS recipe cannot yet build static library. Contributions are welcome.")
        if not self.options["nspr"].shared:
            raise ConanInvalidConfiguration("NSS cannot link to static NSPR. Please use option nspr:shared=True")
        if msvc_runtime_flag(self) == "MTd":
            raise ConanInvalidConfiguration("NSS recipes does not support MTd runtime. Contributions are welcome.")
        if not self.options["sqlite3"].shared:
            raise ConanInvalidConfiguration("NSS cannot link to static sqlite. Please use option sqlite3:shared=True")
        if self.settings.arch in ["armv8", "armv8.3"] and self.settings.os in ["Macos"]:
            raise ConanInvalidConfiguration("Macos ARM64 builds not yet supported. Contributions are welcome.")


    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    @property
    def _make_args(self):
        args = []
        if self.settings.arch in ["x86_64"]:
            args.append("USE_64=1")
            if self.settings.os == "Macos":
                args.append("CPU_ARCH=i386")
            else:
                args.append("CPU_ARCH=x86_64")
        if self.settings.arch in ["armv8", "armv8.3"]:
            args.append("USE_64=1")
            args.append("CPU_ARCH=aarch64")
        if self.settings.compiler == "gcc":
            args.append("XCFLAGS=-Wno-array-parameter")
        args.append("NSPR_INCLUDE_DIR=%s" % self.deps_cpp_info["nspr"].include_paths[1])
        args.append("NSPR_LIB_DIR=%s" % self.deps_cpp_info["nspr"].lib_paths[0])

        os_map = {
            "Linux": "Linux",
            "Macos": "Darwin",
            "Windows": "WINNT",
            "FreeBSD": "FreeBSD"
        }

        args.append("OS_TARGET=%s" % os_map.get(str(self.settings.os), "UNSUPPORTED_OS"))
        args.append("OS_ARCH=%s" % os_map.get(str(self.settings.os), "UNSUPPORTED_OS"))
        if self.settings.build_type != "Debug":
            args.append("BUILD_OPT=1")
        if self.settings.compiler == "Visual Studio":
            args.append("NSPR31_LIB_PREFIX=$(NULL)")

        args.append("USE_SYSTEM_ZLIB=1")
        args.append("ZLIB_INCLUDE_DIR=%s" % self.deps_cpp_info["zlib"].include_paths[0])


        def adjust_path(path, settings):
            """
            adjusts path to be safely passed to the compiler command line
            for Windows bash, ensures path is in format according to the subsystem
            for path with spaces, places double quotes around it
            converts slashes to backslashes, or vice versa
            """
            compiler = _base_compiler(settings)
            if str(compiler) == 'Visual Studio':
                path = path.replace('/', '\\')
            else:
                path = path.replace('\\', '/')
            return '"%s"' % path if ' ' in path else path

        def _base_compiler(settings):
            return settings.get_safe("compiler.base") or settings.get_safe("compiler")

        def _format_library_paths(library_paths, settings):
            compiler = _base_compiler(settings)
            pattern = "-LIBPATH:%s" if str(compiler) == 'Visual Studio' else "-L%s"
            return [pattern % adjust_path(library_path, settings)
                    for library_path in library_paths if library_path]


        def _format_libraries(libraries, settings):
            result = []
            compiler = settings.get_safe("compiler")
            compiler_base = settings.get_safe("compiler.base")
            for library in libraries:
                if str(compiler) == 'Visual Studio' or str(compiler_base) == 'Visual Studio':
                    if not library.endswith(".lib"):
                        library += ".lib"
                    result.append(library)
                else:
                    result.append("-l%s" % library)
            return result


        args.append("\"ZLIB_LIBS=%s\"" % " ".join(
            _format_libraries(self.deps_cpp_info["zlib"].libs, self.settings) +
            _format_library_paths(self.deps_cpp_info["zlib"].lib_paths, self.settings)))
        args.append("NSS_DISABLE_GTESTS=1")
        args.append("NSS_USE_SYSTEM_SQLITE=1")
        args.append("SQLITE_INCLUDE_DIR=%s" % self.deps_cpp_info["sqlite3"].include_paths[0])
        args.append("SQLITE_LIB_DIR=%s" % self.deps_cpp_info["sqlite3"].lib_paths[0])
        args.append("NSDISTMODE=copy")
        if tools.cross_building(self):
            args.append("CROSS_COMPILE=1")
        return args


    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        with tools.chdir(os.path.join(self._source_subfolder, "nss")):
            with tools.vcvars(self) if self.settings.compiler == "Visual Studio" else tools.no_op():
                self.run("make %s" % " ".join(self._make_args), run_environment=True)

    def package(self):
        self.copy("COPYING", src = os.path.join(self._source_subfolder, "nss"), dst = "licenses")
        with tools.chdir(os.path.join(self._source_subfolder, "nss")):
            self.run("make install %s" % " ".join(self._make_args))
        self.copy("*",
                  src=os.path.join(self._source_subfolder, "dist", "public", "nss"),
                  dst="include")
        for d in os.listdir(os.path.join(self._source_subfolder, "dist")):
            if d in ["private","public"]:
                continue
            f = os.path.join(self._source_subfolder, "dist", d)
            if not os.path.isdir(f):
                continue
            self.copy("*", src = f)

        for dll_file in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
            tools.files.rename(self, dll_file, os.path.join(self.package_folder, "bin", os.path.basename(dll_file)))

        if self.options.shared:
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.a")
        else:
            tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.so")
            tools.files.rm(self, os.path.join(self.package_folder, "bin"), "*.dll")



    def package_info(self):

        def _library_name(lib,vers):
            if self.options.shared:
                return "%s%s" % (lib,vers)
            else:
                return lib
        self.cpp_info.components["libnss"].libs.append(_library_name("nss", 3))
        self.cpp_info.components["libnss"].requires = ["nssutil", "nspr::nspr"]

        self.cpp_info.components["nssutil"].libs = [_library_name("nssutil", 3)]
        self.cpp_info.components["nssutil"].requires = ["nspr::nspr"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["nssutil"].system_libs = ["pthread"]

        self.cpp_info.components["softokn"].libs = [_library_name("softokn", 3)]
        self.cpp_info.components["softokn"].requires = ["sqlite3::sqlite3", "nssutil", "nspr::nspr"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["softokn"].system_libs = ["pthread"]

        self.cpp_info.components["nssdbm"].libs = [_library_name("nssdbm", 3)]
        self.cpp_info.components["nssdbm"].requires = ["nspr::nspr", "nssutil"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["nssdbm"].system_libs = ["pthread"]

        self.cpp_info.components["smime"].libs = [_library_name("smime", 3)]
        self.cpp_info.components["smime"].requires = ["nspr::nspr", "libnss", "nssutil"]

        self.cpp_info.components["ssl"].libs = [_library_name("ssl", 3)]
        self.cpp_info.components["ssl"].requires = ["nspr::nspr", "libnss", "nssutil"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ssl"].system_libs = ["pthread"]

        self.cpp_info.components["nss_executables"].requires = ["zlib::zlib"]

        self.cpp_info.set_property("pkg_config_name", "nss")
