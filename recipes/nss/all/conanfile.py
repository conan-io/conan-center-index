from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import msvc_runtime_flag, VCVars, is_msvc
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import get, chdir, rename, rm, copy
from conan.tools.build import cross_building
import os
import glob

required_conan_version = ">=1.59"

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
            self.options.rm_safe("fPIC")

    def build_requirements(self):
        if is_msvc(self) and not self.conf.get("tools.microsoft.bash:path"):
            self.tool_requires("msys2/cci.latest")
        if self.settings.os == "Windows":
            self.tool_requires("mozilla-build/3.3")
        if hasattr(self, "settings_build"):
            self.tool_requires("sqlite3/<host_version>")
        self.tool_requires("nspr/<host_version>")

    def configure(self):
        self.options["nspr"].shared = True
        self.options["sqlite3"].shared = True

        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def requirements(self):
        self.requires("nspr/4.35")
        self.requires("sqlite3/[>=3.41 <4]")
        self.requires("zlib/[>=1.2.13 <2]")

    def validate(self):
        if not self.options.shared:
            raise ConanInvalidConfiguration("NSS recipe cannot yet build static library. Contributions are welcome.")
        if not self.dependencies["nspr"].options.shared:
            raise ConanInvalidConfiguration("NSS cannot link to static NSPR. Please use option nspr:shared=True")
        if msvc_runtime_flag(self) == "MTd":
            raise ConanInvalidConfiguration("NSS recipes does not support MTd runtime. Contributions are welcome.")
        if not self.dependencies["sqlite3"].options.shared:
            raise ConanInvalidConfiguration("NSS cannot link to static sqlite. Please use option sqlite3:shared=True")
        if self.settings.arch in ["armv8", "armv8.3"] and self.settings.os in ["Macos"]:
            raise ConanInvalidConfiguration("Macos ARM64 builds not yet supported. Contributions are welcome.")
        if Version(self.version) < "3.74":
            if self.settings.compiler == "clang" and Version(self.settings.compiler.version) >= 13:
                raise ConanInvalidConfiguration("nss < 3.74 requires clang < 13 .")


    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

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

        args.append("NSPR_INCLUDE_DIR=%s" % self.dependencies["nspr"].cpp_info.aggregated_components().includedirs[1])
        args.append("NSPR_LIB_DIR=%s" % self.dependencies["nspr"].cpp_info.aggregated_components().libdirs[0])

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
        if is_msvc(self):
            args.append("NSPR31_LIB_PREFIX=$(NULL)")

        args.append("USE_SYSTEM_ZLIB=1")
        args.append("ZLIB_INCLUDE_DIR=%s" % self.dependencies["zlib"].cpp_info.aggregated_components().includedirs[0])


        def adjust_path(path, settings):
            """
            adjusts path to be safely passed to the compiler command line
            for Windows bash, ensures path is in format according to the subsystem
            for path with spaces, places double quotes around it
            converts slashes to backslashes, or vice versa
            """
            if is_msvc(self):
                path = path.replace('/', '\\')
            else:
                path = path.replace('\\', '/')
            return '"%s"' % path if ' ' in path else path

        def _format_library_paths(library_paths, settings):
            pattern = "-LIBPATH:%s" if is_msvc(self) else "-L%s"
            return [pattern % adjust_path(library_path, settings)
                    for library_path in library_paths if library_path]


        def _format_libraries(libraries, settings):
            result = []
            for library in libraries:
                if is_msvc(self):
                    if not library.endswith(".lib"):
                        library += ".lib"
                    result.append(library)
                else:
                    result.append(f"-l{library}")
            return result


        args.append("\"ZLIB_LIBS=%s\"" % " ".join(
            _format_libraries(self.dependencies["zlib"].cpp_info.aggregated_components().libs, self.settings) +
            _format_library_paths(self.dependencies["zlib"].cpp_info.aggregated_components().libdirs, self.settings)))
        args.append("NSS_DISABLE_GTESTS=1")
        args.append("NSS_USE_SYSTEM_SQLITE=1")
        args.append("SQLITE_INCLUDE_DIR=%s" % self.dependencies["sqlite3"].cpp_info.aggregated_components().includedirs[0])
        args.append("SQLITE_LIB_DIR=%s" % self.dependencies["sqlite3"].cpp_info.aggregated_components().libdirs[0])
        args.append("NSDISTMODE=copy")
        if cross_building(self):
            args.append("CROSS_COMPILE=1")
        return args


    def generate(self):
        ms = VCVars(self)
        ms.generate()
        vbe = VirtualBuildEnv(self)
        vbe.generate()
        if not cross_building(self):
            vre = VirtualRunEnv(self)
            vre.generate(scope="build")
  
    def build(self):
        with chdir(self, os.path.join(self._source_subfolder, "nss")):
            self.run("make %s" % " ".join(self._make_args))

    def package(self):
        copy(self, "COPYING", src=os.path.join(self._source_subfolder, "nss"), dst="licenses")
        with chdir(self, os.path.join(self._source_subfolder, "nss")):
            self.run("make install %s" % " ".join(self._make_args))
        copy(self, "*", src=os.path.join(self._source_subfolder, "dist", "public", "nss"), dst="include")
        for d in os.listdir(os.path.join(self._source_subfolder, "dist")):
            if d in ["private","public"]:
                continue
            f = os.path.join(self._source_subfolder, "dist", d)
            if not os.path.isdir(f):
                continue
            copy(self, "*", src=f, dst="")

        for dll_file in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
            rename(self, dll_file, os.path.join(self.package_folder, "bin", os.path.basename(dll_file)))

        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
        else:
            rm(self, "*.so", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        def _library_name(lib,vers):
            return f"{lib}{vers}" if self.options.shared else lib

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
