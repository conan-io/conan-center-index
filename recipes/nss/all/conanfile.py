import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv, Environment
from conan.tools.files import chdir, copy, get, rm, replace_in_file, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, VCVars, unix_path

required_conan_version = ">=1.60.0 <2.0 || >=2.0.6"


class NSSConan(ConanFile):
    name = "nss"
    license = "MPL-2.0"
    homepage = "https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Network Security Services"
    topics = ("network", "security", "crypto", "ssl")

    # TODO: static builds are supported, but the necessary package_info() is complex
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        self.options["nspr"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nspr/4.35", transitive_headers=True, transitive_libs=True)
        self.requires("sqlite3/[>=3.41.0 <4]")
        self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if not self.dependencies["nspr"].options.shared:
            raise ConanInvalidConfiguration("NSS cannot link to static NSPR. Please use option nspr:shared=True")

    def build_requirements(self):
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if self.settings.os == "Windows":
            self.tool_requires("mozilla-build/4.0.2")
        self.tool_requires("cpython/3.12.2")
        self.tool_requires("ninja/[>=1.10.2 <2]")
        self.tool_requires("sqlite3/<host_version>")
        if not can_run(self):
            # Needed for shlibsign executable
            self.tool_requires(f"nss/{self.version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    @property
    def _vs_year(self):
        compiler_version = str(self.settings.compiler.version)
        return {
            "180": "2013",
            "190": "2015",
            "191": "2017",
            "192": "2019",
            "193": "2022",
            "194": "2022",
        }.get(compiler_version)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        vc = VCVars(self)
        vc.generate()

        env = Environment()

        compilers_from_conf = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)
        buildenv_vars = VirtualBuildEnv(self).vars()
        cc = compilers_from_conf.get("c", buildenv_vars.get("CC"))
        if cc:
            env.define("CC", unix_path(self, cc))
        strip = compilers_from_conf.get("strip", buildenv_vars.get("STRIP"))
        if strip:
            env.define("STRIP", unix_path(self, strip))
        cxx = compilers_from_conf.get("cpp", buildenv_vars.get("CXX"))
        if cc:
            env.define("CXX", unix_path(self, cxx))

        # Add temporary site-packages to PYTHONPATH for gyp-next
        env.prepend_path("PYTHONPATH", self._site_packages_dir)
        if self.settings.os == "Windows":
            # An additional forward-slash path is needed for MSYS2 bash
            env.prepend_path("PYTHONPATH", self._site_packages_dir.replace("\\", "/"))
        env.prepend_path("PATH", os.path.join(self._site_packages_dir, "bin"))

        # For 'shlibsign -v -i <dist_dir>/lib/libfreebl3.so' etc to work during build
        env.prepend_path("LD_LIBRARY_PATH", os.path.join(self._dist_dir, "lib"))

        if is_msvc(self):
            env.define("GYP_MSVS_VERSION", self._vs_year)

        env.vars(self, scope="build").save_script("conan_paths")

    @property
    def _dist_dir(self):
        # location for installed lib/ and bin/ subdirs
        dist_subdir = "Debug" if self.settings.build_type == "Debug" else "Release"
        return os.path.join(self.source_folder, "dist", dist_subdir)

    @property
    def _site_packages_dir(self):
        return os.path.join(self.build_folder, "site-packages")

    def _pip_install(self, packages):
        site_packages_dir = self._site_packages_dir.replace("\\", "/")
        self.run(f"python -m pip install {' '.join(packages)} --no-cache-dir --target={site_packages_dir} --index-url https://pypi.org/simple",)

    def _patch_sources(self):
        def _format_library_paths(library_paths):
            flag = "-LIBPATH:" if is_msvc(self) else "-L"
            return [flag + unix_path(self, library_path)
                    for library_path in library_paths if library_path]

        def _format_libraries(libraries, libdir):
            result = []
            for library in libraries:
                if is_msvc(self):
                    if not library.endswith(".lib"):
                        library += ".lib"
                    if libdir is not None:
                        library = os.path.join(libdir, library).replace("\\", "/")
                    result.append(library)
                else:
                    result.append(f"-l{library}")
            return result

        sqlite_info = self.dependencies["sqlite3"].cpp_info.aggregated_components()
        sqlite_flags = " ".join([f"-I{unix_path(self, sqlite_info.includedir)}"] +
                                _format_libraries(sqlite_info.libs, sqlite_info.libdir) +
                                _format_libraries(sqlite_info.system_libs, None) +
                                _format_library_paths(sqlite_info.libdirs))
        replace_in_file(self, os.path.join(self.source_folder, "nss", "lib", "sqlite", "sqlite.gyp"),
                        "'libraries': ['<(sqlite_libs)'],",
                        f"'libraries': ['{sqlite_flags}'],")

        zlib_info = self.dependencies["zlib"].cpp_info.aggregated_components()
        zlib_flags = " ".join([f"-I{unix_path(self, zlib_info.includedir)}"] +
                                _format_libraries(zlib_info.libs, zlib_info.libdir) +
                                _format_libraries(zlib_info.system_libs, None) +
                                _format_library_paths(zlib_info.libdirs))
        replace_in_file(self, os.path.join(self.source_folder, "nss", "lib", "zlib", "zlib.gyp"),
                        "'libraries': ['<@(zlib_libs)'],",
                        f"'libraries': ['{zlib_flags}'],")

        # NSPR Windows libs on CCI don't include a lib prefix
        replace_in_file(self, os.path.join(self.source_folder, "nss", "coreconf", "config.gypi"),
                        "'nspr_libs%': ['libnspr4.lib', 'libplc4.lib', 'libplds4.lib'],",
                        "'nspr_libs%': ['nspr4.lib', 'plc4.lib', 'plds4.lib'],")

        # Don't let shlibsign.py set LD_LIBRARY_PATH to the incorrect value.
        replace_in_file(self, os.path.join(self.source_folder, "nss", "coreconf", "shlibsign.py"),
                        "env['LD_LIBRARY_PATH']", "pass # env['LD_LIBRARY_PATH']")
        if not can_run(self):
            shlibsign = os.path.join(self.dependencies.build["nss"].package_folder, "bin", "shlibsign").replace("\\", "/")
            replace_in_file(self, os.path.join(self.source_folder, "nss", "coreconf", "shlibsign.py"),
                            "os.path.join(bin_path, 'shlibsign')", f"'{shlibsign}'")

    @property
    def _arch(self):
        if self.settings.arch == "x86_64":
            return "x64"
        elif self.settings.arch == "x86":
            return "ia32"
        elif self.settings.arch in ["armv8", "armv8.3"]:
            return "aarch64"
        return str(self.settings.arch)

    @property
    def _build_args(self):
        # https://github.com/nss-dev/nss/blob/master/help.txt
        args = []
        args.append("--disable-tests")
        args.append(f"--target={self._arch}")
        args.append(f"-Dtarget_arch={self._arch}")
        args.append("-Dstatic_libs=" + ("1" if not self.options.get_safe("shared", True) else "0"))
        if not self.options.get_safe("shared", True):
            args.append("--static")
        if self.settings.build_type != "Debug":
            args.append("--opt")
        if is_msvc(self):
            args.append("--msvc")
        nspr_root = self.dependencies["nspr"].package_folder
        nspr_includedir = unix_path(self, os.path.join(nspr_root, "include", "nspr"))
        nspr_libdir = unix_path(self, os.path.join(nspr_root, "lib"))
        args.append(f"--with-nspr={nspr_includedir}:{nspr_libdir}")
        args.append("--system-sqlite")
        args.append("--enable-legacy-db")  # for libnssdbm3
        return args

    def build(self):
        self._patch_sources()
        self._pip_install(["gyp-next"])
        self.run(f"gyp --version")

        with chdir(self, os.path.join(self.source_folder, "nss")):
            self.run(f"./build.sh {' '.join(self._build_args)}")

    def package(self):
        copy(self, "COPYING", src=os.path.join(self.source_folder, "nss"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
             src=os.path.join(self.source_folder, "dist", "public"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "*", os.path.join(self._dist_dir, "bin"), os.path.join(self.package_folder, "bin"))
        for pattern in ["*.a", "*.lib", "*.so", "*.dylib"]:
            copy(self, pattern, os.path.join(self._dist_dir, "lib"), os.path.join(self.package_folder, "lib"))
        copy(self, "*.dll", os.path.join(self._dist_dir, "lib"), os.path.join(self.package_folder, "bin"))
        if not self.options.get_safe("shared", True):
            rm(self, "*.so", os.path.join(self.package_folder, "lib"))
            rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
        else:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        # Since the project does not export any .pc files,
        # we will rely on the .pc files created by Fedora
        # https://src.fedoraproject.org/rpms/nss/tree/rawhide
        # and Debian
        # https://salsa.debian.org/mozilla-team/nss/-/tree/master/debian
        # instead.

        self.cpp_info.set_property("pkg_config_name", "_nss")

        # https://src.fedoraproject.org/rpms/nss/blob/rawhide/f/nss-util.pc.in
        self.cpp_info.components["nssutil"].set_property("pkg_config_name", "nss-util")
        self.cpp_info.components["nssutil"].libs = ["nssutil3"]
        self.cpp_info.components["nssutil"].includedirs.append(os.path.join("include", "nss"))
        self.cpp_info.components["nssutil"].requires = ["nspr::nspr"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["nssutil"].system_libs = ["pthread", "dl"]

        # https://src.fedoraproject.org/rpms/nss/blob/rawhide/f/nss.pc.in
        self.cpp_info.components["libnss"].set_property("pkg_config_name", "nss")
        self.cpp_info.components["libnss"].libs = ["ssl3", "smime3", "nss3"]
        self.cpp_info.components["libnss"].includedirs.append(os.path.join("include", "nss"))
        self.cpp_info.components["libnss"].requires = ["nspr::nspr", "nssutil"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libnss"].system_libs = ["pthread", "dl"]

        # https://src.fedoraproject.org/rpms/nss/blob/rawhide/f/nss-softokn.pc.in
        self.cpp_info.components["softokn"].set_property("pkg_config_name", "nss-softokn")
        self.cpp_info.components["softokn"].libs = ["freebl3", "nssdbm3", "softokn3"]
        self.cpp_info.components["softokn"].includedirs.append(os.path.join("include", "nss"))
        self.cpp_info.components["softokn"].requires = ["nspr::nspr", "sqlite3::sqlite3", "nssutil"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["softokn"].system_libs = ["pthread", "dl"]

        self.cpp_info.components["nss_executables"].requires = ["zlib::zlib", "nspr::nspr", "sqlite3::sqlite3"]
