import json
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import can_run
from conan.tools.env import VirtualBuildEnv, Environment, VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, export_conandata_patches, apply_conandata_patches, rmdir, save, load, collect_libs
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

    # FIXME: NSS_Init() fails in test_package for static builds
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_legacy_db": [True, False],
    }
    default_options = {
        "enable_legacy_db": False,
    }

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
        # Remove vendored sources
        rmdir(self, os.path.join("nss", "lib", "sqlite"))
        rmdir(self, os.path.join("nss", "lib", "zlib"))

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

    @property
    def _dist_dir(self):
        return os.path.join(self.build_folder, "dist")

    @property
    def _target_build_dir(self):
        return os.path.join(self.build_folder, "out", "Debug" if self.settings.build_type == "Debug" else "Release")

    @property
    def _arch(self):
        if self.settings.arch == "x86_64":
            return "x64"
        elif self.settings.arch == "x86":
            return "ia32"
        elif self.settings.arch in ["armv8", "armv8.3"]:
            return "aarch64"
        return str(self.settings.arch)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if can_run(self):
            # The built shlibsign executable needs to find shared libs
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        vc = VCVars(self)
        vc.generate()


        nspr_root = self.dependencies["nspr"].package_folder
        nspr_includedir = unix_path(self, os.path.join(nspr_root, "include", "nspr"))
        nspr_libdir = unix_path(self, os.path.join(nspr_root, "lib"))

        gyp_args = {}
        gyp_args["nss_dist_dir"] = unix_path(self, self._dist_dir)
        gyp_args["nss_dist_obj_dir"] = unix_path(self, self._dist_dir)
        gyp_args["opt_build"] = 1 if self.settings.build_type != "Debug" else 0
        gyp_args["static_libs"] = 1 if not self.options.get_safe("shared", True) else 0
        gyp_args["target_arch"] = self._arch
        gyp_args["disable_tests"] = 1
        gyp_args["no_local_nspr"] = 1
        gyp_args["nspr_include_dir"] = nspr_includedir
        gyp_args["nspr_lib_dir"] = nspr_libdir
        gyp_args["use_system_sqlite"] = 1
        gyp_args["use_system_zlib"] = 1
        gyp_args["disable_dbm"] = 0 if self.options.enable_legacy_db else 1
        gyp_args["enable_sslkeylogfile"] = 1  # default in build.sh
        save(self, "gyp_args.txt", "\n".join(f"-D{k}={v}" for k, v in gyp_args.items()))

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
            env.define("CCC", unix_path(self, cxx))

        if is_msvc(self):
            env.define("GYP_MSVS_VERSION", self._vs_year)

        # For 'shlibsign -v -i <dist_dir>/lib/libfreebl3.so' etc to work during build
        env.prepend_path("LD_LIBRARY_PATH", os.path.join(self._dist_dir, "lib"))

        # Add temporary site-packages to PYTHONPATH for gyp-next
        env.prepend_path("PYTHONPATH", self._site_packages_dir)
        if self.settings.os == "Windows":
            # An additional forward-slash path is needed for MSYS2 bash
            env.prepend_path("PYTHONPATH", self._site_packages_dir.replace("\\", "/"))
        env.prepend_path("PATH", os.path.join(self._site_packages_dir, "bin"))

        env.vars(self, scope="build").save_script("conan_paths")

    @property
    def _site_packages_dir(self):
        return os.path.join(self.build_folder, "site-packages")

    def _pip_install(self, packages):
        site_packages_dir = self._site_packages_dir.replace("\\", "/")
        self.run(f"python -m pip install {' '.join(packages)} --no-cache-dir --target={site_packages_dir} --index-url https://pypi.org/simple",)

    def _write_conan_gyp_target(self, conan_dep, target_name, file_name):
        def _format_libs(libraries, libdir=None):
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

        lib_dir = os.path.join(self.source_folder, "nss", "lib", file_name)
        cpp_info = self.dependencies[conan_dep].cpp_info.aggregated_components()
        build_gyp = {
            "includes": ["../../coreconf/config.gypi"],
            "targets": [{
                "target_name": target_name,
                "type": "none",
                "direct_dependent_settings": {
                    "defines": cpp_info.defines,
                    "include_dirs": [cpp_info.includedir.replace("\\", "/")],
                    "link_settings": {
                        "libraries": _format_libs(cpp_info.libs, cpp_info.libdir.replace("\\", "/")) + _format_libs(cpp_info.system_libs),
                        "library_dirs": [libdir.replace("\\", "/") for libdir in cpp_info.libdirs],
                    },
                }
            }],
        }
        save(self, os.path.join(lib_dir, f"{file_name}.gyp"), json.dumps(build_gyp, indent=2))

        exports_gyp = {
            "includes": ["../../coreconf/config.gypi"],
            "targets": [{
                "target_name": f"lib_{file_name}_exports",
                "type": "none",
            }],
        }
        save(self, os.path.join(lib_dir, "exports.gyp"), json.dumps(exports_gyp, indent=2))

    def _patch_sources(self):
        self._write_conan_gyp_target("sqlite3", "sqlite3", "sqlite")
        self._write_conan_gyp_target("zlib", "nss_zlib", "zlib")

        # NSPR Windows libs on CCI don't include a lib prefix
        replace_in_file(self, os.path.join(self.source_folder, "nss", "coreconf", "config.gypi"),
                        "'nspr_libs%': ['libnspr4.lib', 'libplc4.lib', 'libplds4.lib'],",
                        "'nspr_libs%': ['nspr4.lib', 'plc4.lib', 'plds4.lib'],")

        # Don't let shlibsign.py set LD_LIBRARY_PATH to an incorrect value.
        replace_in_file(self, os.path.join(self.source_folder, "nss", "coreconf", "shlibsign.py"),
                        "env['LD_LIBRARY_PATH']", "pass # env['LD_LIBRARY_PATH']")
        if not can_run(self):
            shlibsign = os.path.join(self.dependencies.build["nss"].package_folder, "bin", "shlibsign").replace("\\", "/")
            replace_in_file(self, os.path.join(self.source_folder, "nss", "coreconf", "shlibsign.py"),
                            "os.path.join(bin_path, 'shlibsign')", f"'{shlibsign}'")

    def build(self):
        self._patch_sources()
        self._pip_install(["gyp-next"])
        args = load(self, os.path.join(self.generators_folder, "gyp_args.txt")).replace("\n", " ")
        cmd = f'gyp -f ninja nss.gyp --depth=. --generator-output="{unix_path(self, self.build_folder)}" ' + args
        if is_msvc(self):
            cmd = f"bash -c 'target_arch={self._arch} source coreconf/msvc.sh; {cmd}'"
        self.run(cmd, cwd=os.path.join(self.source_folder, "nss"))
        self.run("ninja", cwd=self._target_build_dir)

    def package(self):
        copy(self, "COPYING", src=os.path.join(self.source_folder, "nss"), dst=os.path.join(self.package_folder, "licenses"))

        copy(self, "*",
             src=os.path.join(self._dist_dir, "public"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "*",
             src=os.path.join(self._dist_dir, "private", "nss"),
             dst=os.path.join(self.package_folder, "include", "nss", "private"))

        # Tools are always linked against shared libs only
        if self.options.get_safe("shared", True):
            exe_pattern = "*.exe" if self.settings.os == "Windows" else "*"
            copy(self, exe_pattern, os.path.join(self._dist_dir, "bin"), os.path.join(self.package_folder, "bin"))

        lib_dir = os.path.join(self._dist_dir, "lib")
        if self.options.get_safe("shared", True):
            for pattern in ["*.so", "*.chk", "*.dylib", "*.dll.lib"]:
                copy(self, pattern, lib_dir, os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll", lib_dir, os.path.join(self.package_folder, "bin"))
        else:
            copy(self, "*.a", lib_dir, os.path.join(self.package_folder, "lib"))
            copy(self, "*.lib", lib_dir, os.path.join(self.package_folder, "lib"), excludes="*.dll.lib")
        fix_apple_shared_install_name(self)

    def package_info(self):
        # Since the project does not export any .pc files,
        # we will rely on the .pc files created by Fedora
        # https://src.fedoraproject.org/rpms/nss/tree/rawhide
        # and Debian
        # https://salsa.debian.org/mozilla-team/nss/-/tree/master/debian
        # instead.

        # Do not use
        self.cpp_info.set_property("pkg_config_name", "_nss")

        # https://src.fedoraproject.org/rpms/nss/blob/rawhide/f/nss.pc.in
        self.cpp_info.components["nss_pc"].set_property("pkg_config_name", "nss")
        self.cpp_info.components["nss_pc"].requires = ["libnss", "ssl", "smime"]

        self.cpp_info.components["libnss"].libs = ["nss3"]
        self.cpp_info.components["libnss"].includedirs.append(os.path.join("include", "nss"))
        self.cpp_info.components["libnss"].requires = ["util", "nspr::nspr"]

        # https://src.fedoraproject.org/rpms/nss/blob/rawhide/f/nss-util.pc.in
        self.cpp_info.components["util"].set_property("pkg_config_name", "nss-util")
        self.cpp_info.components["util"].libs = ["nssutil3"]
        self.cpp_info.components["util"].includedirs.append(os.path.join("include", "nss"))
        self.cpp_info.components["util"].requires = ["nspr::nspr"]

        # https://src.fedoraproject.org/rpms/nss/blob/rawhide/f/nss-softokn.pc.in
        self.cpp_info.components["softokn"].set_property("pkg_config_name", "nss-softokn")
        self.cpp_info.components["softokn"].libs = ["softokn3"]
        self.cpp_info.components["softokn"].requires = ["libnss", "freebl", "sqlite3::sqlite3"]
        if self.options.enable_legacy_db:
            self.cpp_info.components["softokn"].requires.append("dbm")

        self.cpp_info.components["ssl"].libs = ["ssl3"]
        self.cpp_info.components["ssl"].requires = ["libnss", "util", "nspr::nspr"]

        self.cpp_info.components["smime"].libs = ["smime3"]
        self.cpp_info.components["smime"].requires = ["libnss", "util", "nspr::nspr"]

        self.cpp_info.components["freebl"].libs = ["freebl3"]
        self.cpp_info.components["freebl"].includedirs.append(os.path.join("include", "nss"))

        if self.options.enable_legacy_db:
            self.cpp_info.components["dbm"].libs = ["nssdbm3"]
            self.cpp_info.components["dbm"].requires = ["util", "nspr::nspr"]

        # There are also nssckbi and nsssysinit shared libs, but these are meant to be loaded dynamically

        if not self.options.get_safe("shared", True):
            static_libs = collect_libs(self)

            self.cpp_info.components["libnss"].libs = ["nss_static"]
            self.cpp_info.components["libnss"].requires += [
                "base", "certdb", "certhi", "cryptohi", "dev", "pk11wrap", "pki",
            ]

            freebl_private = [name for name in static_libs if
                              name.startswith("freebl") or "c_lib" in name or "gcm-" in name or "hw-acc-crypto-" in name]
            self.cpp_info.components["freebl"].libs = ["freebl", "freebl_static"] + freebl_private

            self.cpp_info.components["smime"].libs = ["smime"]
            self.cpp_info.components["softokn"].libs = ["softokn", "softokn_static"]
            self.cpp_info.components["ssl"].libs = ["ssl"]
            self.cpp_info.components["util"].libs = ["nssutil"]

            if self.options.enable_legacy_db:
                self.cpp_info.components["dbm"].libs = ["nssdbm"]

            # Static-only libs
            self.cpp_info.components["base"].libs = ["nssb"]
            self.cpp_info.components["certdb"].libs = ["certdb"]
            self.cpp_info.components["certhi"].libs = ["certhi"]
            self.cpp_info.components["ckfw"].libs = ["nssckfw"]
            self.cpp_info.components["crmf"].libs = ["crmf"]
            self.cpp_info.components["cryptohi"].libs = ["cryptohi"]
            self.cpp_info.components["dev"].libs = ["nssdev"]
            self.cpp_info.components["jar"].libs = ["jar"]
            self.cpp_info.components["mozpkix"].libs = ["mozpkix"]
            self.cpp_info.components["mozpkix-testlib"].libs = ["mozpkix-testlib"]
            self.cpp_info.components["pk11wrap"].libs = ["pk11wrap", "pk11wrap_static"]
            self.cpp_info.components["pkcs7"].libs = ["pkcs7"]
            self.cpp_info.components["pkcs12"].libs = ["pkcs12"]
            self.cpp_info.components["pki"].libs = ["nsspki"]

            # Not built by default
            # self.cpp_info.components["sysinit"].libs = ["nsssysinit_static"]

        self.cpp_info.components["tools"].requires = ["zlib::zlib", "nspr::nspr", "sqlite3::sqlite3"]
