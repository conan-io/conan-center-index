import glob
import hashlib
import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building, stdcpp_library, check_min_cppstd
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rename, replace_in_file, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.57.0"


class ICUConan(ConanFile):
    name = "icu"
    homepage = "http://site.icu-project.org"
    license = "ICU"
    description = "ICU is a mature, widely used set of C/C++ and Java libraries " \
                  "providing Unicode and Globalization support for software applications."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("icu4c", "i see you", "unicode")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "data_packaging": ["files", "archive", "library", "static"],
        "with_dyload": [True, False],
        "dat_package_file": [None, "ANY"],
        "with_icuio": [True, False],
        "with_extras": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "data_packaging": "archive",
        "with_dyload": True,
        "dat_package_file": None,
        "with_icuio": True,
        "with_extras": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
        }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _enable_icu_tools(self):
        return self.settings.os not in ["iOS", "tvOS", "watchOS", "Emscripten"]

    @property
    def _with_unit_tests(self):
        return not self.conf.get("tools.build:skip_test", default=True, check_type=bool)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.data_packaging

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if Version(self.version) >= "74.1":
            self.license = "Unicode-3.0"

    def validate(self):
        if self.options.dat_package_file:
            if not os.path.exists(str(self.options.dat_package_file)):
                raise ConanInvalidConfiguration("Non-existent dat_package_file specified")
        if Version(self.version) >= "75.1":
            if self.settings.compiler.cppstd:
                check_min_cppstd(self, self._min_cppstd)
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def layout(self):
        basic_layout(self, src_folder="src")

    @staticmethod
    def _sha256sum(file_path):
        m = hashlib.sha256()
        with open(file_path, "rb") as fh:
            for data in iter(lambda: fh.read(8192), b""):
                m.update(data)
        return m.hexdigest()

    def package_id(self):
        if self.info.options.dat_package_file:
            self.info.options.dat_package_file = self._sha256sum(str(self.info.options.dat_package_file))

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

        if cross_building(self) and hasattr(self, "settings_build"):
            self.tool_requires(str(self.ref))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if check_min_vs(self, "180", raise_invalid=False):
            tc.extra_cflags.append("-FS")
            tc.extra_cxxflags.append("-FS")
        if not self.options.shared:
            tc.extra_defines.append("U_STATIC_IMPLEMENTATION")
        if is_apple_os(self):
            tc.extra_defines.append("_DARWIN_C_SOURCE")
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--datarootdir=${prefix}/lib", # do not use share
            f"--enable-release={yes_no(self.settings.build_type != 'Debug')}",
            f"--enable-debug={yes_no(self.settings.build_type == 'Debug')}",
            f"--enable-dyload={yes_no(self.options.with_dyload)}",
            f"--enable-extras={yes_no(self.options.with_extras)}",
            f"--enable-icuio={yes_no(self.options.with_icuio)}",
            "--disable-layoutex",
            "--disable-layout",
            f"--enable-tools={yes_no(self._enable_icu_tools)}",
            f"--enable-tests={yes_no(self._with_unit_tests)}",
            "--disable-samples",
        ])
        if cross_building(self):
            base_path = unix_path(self, self.dependencies.build["icu"].package_folder)
            tc.configure_args.append(f"--with-cross-build={base_path}")
            if self.settings.os in ["iOS", "tvOS", "watchOS"]:
                # ICU build scripts interpret all Apple platforms as 'darwin'.
                # Since this can coincide with the `build` triple, we need to tweak
                # the build triple to avoid the collision and ensure the scripts
                # know we are cross-building.
                host_triplet = f"{str(self.settings.arch)}-apple-darwin"
                build_triplet = f"{str(self._settings_build.arch)}-apple"
                tc.update_configure_args({"--host": host_triplet,
                                          "--build": build_triplet})
        else:
            arch64 = ["x86_64", "sparcv9", "ppc64", "ppc64le", "armv8", "armv8.3", "mips64"]
            bits = "64" if self.settings.arch in arch64 else "32"
            tc.configure_args.append(f"--with-library-bits={bits}")
        if self.settings.os != "Windows":
            # http://userguide.icu-project.org/icudata
            # This is the only directly supported behavior on Windows builds.
            tc.configure_args.append(f"--with-data-packaging={self.options.data_packaging}")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            env.define("CC", "cl -nologo")
            if Version(self.version) < "75.1":
                env.define("CXX", "cl -nologo")
            else:
                env.define("CXX", "cl -nologo -std:c++17")
            if cross_building(self):
                env.define("icu_cv_host_frag", "mh-msys-msvc")
            env.vars(self).save_script("conanbuild_icu_msvc")

    def _patch_sources(self):
        apply_conandata_patches(self)

        if not self._with_unit_tests:
            # Prevent any call to python during configuration, it's only needed for unit tests
            replace_in_file(
                self,
                os.path.join(self.source_folder, "source", "configure"),
                "if test -z \"$PYTHON\"",
                "if true",
            )

        if self._settings_build.os == "Windows":
            # https://unicode-org.atlassian.net/projects/ICU/issues/ICU-20545
            makeconv_cpp = os.path.join(self.source_folder, "source", "tools", "makeconv", "makeconv.cpp")
            replace_in_file(self, makeconv_cpp,
                            "pathBuf.appendPathPart(arg, localError);",
                            "pathBuf.append(\"/\", localError); pathBuf.append(arg, localError);")

        # relocatable shared libs on macOS
        mh_darwin = os.path.join(self.source_folder, "source", "config", "mh-darwin")
        replace_in_file(self, mh_darwin, "-install_name $(libdir)/$(notdir", "-install_name @rpath/$(notdir")
        replace_in_file(self,
            mh_darwin,
            "-install_name $(notdir $(MIDDLE_SO_TARGET)) $(PKGDATA_TRAILING_SPACE)",
            "-install_name @rpath/$(notdir $(MIDDLE_SO_TARGET))",
        )

        # workaround for https://unicode-org.atlassian.net/browse/ICU-20531
        mkdir(self, os.path.join(self.build_folder, "data", "out", "tmp"))

        # workaround for "No rule to make target 'out/tmp/dirs.timestamp'"
        save(self, os.path.join(self.build_folder, "data", "out", "tmp", "dirs.timestamp"), "")

    def build(self):
        self._patch_sources()

        if self.options.dat_package_file:
            dat_package_file = glob.glob(os.path.join(self.source_folder, "source", "data", "in", "*.dat"))
            if dat_package_file:
                shutil.copy(str(self.options.dat_package_file), dat_package_file[0])

        autotools = Autotools(self)
        autotools.configure(build_script_folder=os.path.join(self.source_folder, "source"))
        autotools.make()
        if self._with_unit_tests:
            autotools.make(target="check")

    @property
    def _data_filename(self):
        vtag = Version(self.version).major
        return f"icudt{vtag}l.dat"

    @property
    def _data_path(self):
        data_dir_name = "icu"
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            data_dir_name += "d"
        data_dir = os.path.join(self.package_folder, "lib", data_dir_name, str(self.version))
        return os.path.join(data_dir, self._data_filename)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        dll_files = glob.glob(os.path.join(self.package_folder, "lib", "*.dll"))
        if dll_files:
            bin_dir = os.path.join(self.package_folder, "bin")
            mkdir(self, bin_dir)
            for dll in dll_files:
                dll_name = os.path.basename(dll)
                rm(self, dll_name, bin_dir)
                rename(self, src=dll, dst=os.path.join(bin_dir, dll_name))

        if self.settings.os != "Windows" and self.options.data_packaging in ["files", "archive"]:
            mkdir(self, os.path.join(self.package_folder, "res"))
            rename(self, src=self._data_path, dst=os.path.join(self.package_folder, "res", self._data_filename))

        # Copy some files required for cross-compiling
        config_dir = os.path.join(self.package_folder, "config")
        copy(self, "icucross.mk", src=os.path.join(self.build_folder, "config"), dst=config_dir)
        copy(self, "icucross.inc", src=os.path.join(self.build_folder, "config"), dst=config_dir)

        rmdir(self, os.path.join(self.package_folder, "lib", "icu"))
        rmdir(self, os.path.join(self.package_folder, "lib", "man"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "ICU")

        prefix = "s" if self.settings.os == "Windows" and not self.options.shared else ""
        suffix = "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""

        # icudata
        self.cpp_info.components["icu-data"].set_property("cmake_target_name", "ICU::data")
        icudata_libname = "icudt" if self.settings.os == "Windows" else "icudata"
        self.cpp_info.components["icu-data"].libs = [f"{prefix}{icudata_libname}{suffix}"]
        if not self.options.shared:
            self.cpp_info.components["icu-data"].defines.append("U_STATIC_IMPLEMENTATION")
            # icu uses c++, so add the c++ runtime
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["icu-data"].system_libs.append(libcxx)

        # Alias of data CMake component
        self.cpp_info.components["icu-data-alias"].set_property("cmake_target_name", "ICU::dt")
        self.cpp_info.components["icu-data-alias"].requires = ["icu-data"]

        # icuuc
        self.cpp_info.components["icu-uc"].set_property("cmake_target_name", "ICU::uc")
        self.cpp_info.components["icu-uc"].set_property("pkg_config_name", "icu-uc")
        self.cpp_info.components["icu-uc"].libs = [f"{prefix}icuuc{suffix}"]
        self.cpp_info.components["icu-uc"].requires = ["icu-data"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["icu-uc"].system_libs = ["m", "pthread"]
            if self.options.with_dyload:
                self.cpp_info.components["icu-uc"].system_libs.append("dl")
        elif self.settings.os == "Windows":
            self.cpp_info.components["icu-uc"].system_libs = ["advapi32"]

        # icui18n
        self.cpp_info.components["icu-i18n"].set_property("cmake_target_name", "ICU::i18n")
        self.cpp_info.components["icu-i18n"].set_property("pkg_config_name", "icu-i18n")
        icui18n_libname = "icuin" if self.settings.os == "Windows" else "icui18n"
        self.cpp_info.components["icu-i18n"].libs = [f"{prefix}{icui18n_libname}{suffix}"]
        self.cpp_info.components["icu-i18n"].requires = ["icu-uc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["icu-i18n"].system_libs = ["m"]

        # Alias of i18n CMake component
        self.cpp_info.components["icu-i18n-alias"].set_property("cmake_target_name", "ICU::in")
        self.cpp_info.components["icu-i18n-alias"].requires = ["icu-i18n"]

        # icuio
        if self.options.with_icuio:
            self.cpp_info.components["icu-io"].set_property("cmake_target_name", "ICU::io")
            self.cpp_info.components["icu-io"].set_property("pkg_config_name", "icu-io")
            self.cpp_info.components["icu-io"].libs = [f"{prefix}icuio{suffix}"]
            self.cpp_info.components["icu-io"].requires = ["icu-i18n", "icu-uc"]

        if self.settings.os != "Windows" and self.options.data_packaging in ["files", "archive"]:
            self.cpp_info.components["icu-data"].resdirs = ["res"]
            data_path = os.path.join(self.package_folder, "res", self._data_filename).replace("\\", "/")
            self.runenv_info.prepend_path("ICU_DATA", data_path)
            if self._enable_icu_tools or self.options.with_extras:
                self.buildenv_info.prepend_path("ICU_DATA", data_path)

        if self._enable_icu_tools:
            # icutu
            self.cpp_info.components["icu-tu"].set_property("cmake_target_name", "ICU::tu")
            self.cpp_info.components["icu-tu"].libs = [f"{prefix}icutu{suffix}"]
            self.cpp_info.components["icu-tu"].requires = ["icu-i18n", "icu-uc"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["icu-tu"].system_libs = ["pthread"]

            # icutest
            self.cpp_info.components["icu-test"].set_property("cmake_target_name", "ICU::test")
            self.cpp_info.components["icu-test"].libs = [f"{prefix}icutest{suffix}"]
            self.cpp_info.components["icu-test"].requires = ["icu-tu", "icu-uc"]

        # TODO: to remove after conan v2
        self.cpp_info.names["cmake_find_package"] = "ICU"
        self.cpp_info.names["cmake_find_package_multi"] = "ICU"
        self.cpp_info.components["icu-data"].names["cmake_find_package"] = "data"
        self.cpp_info.components["icu-data"].names["cmake_find_package_multi"] = "data"
        self.cpp_info.components["icu-data-alias"].names["cmake_find_package"] = "dt"
        self.cpp_info.components["icu-data-alias"].names["cmake_find_package_multi"] = "dt"
        self.cpp_info.components["icu-uc"].names["cmake_find_package"] = "uc"
        self.cpp_info.components["icu-uc"].names["cmake_find_package_multi"] = "uc"
        self.cpp_info.components["icu-i18n"].names["cmake_find_package"] = "i18n"
        self.cpp_info.components["icu-i18n"].names["cmake_find_package_multi"] = "i18n"
        self.cpp_info.components["icu-i18n-alias"].names["cmake_find_package"] = "in"
        self.cpp_info.components["icu-i18n-alias"].names["cmake_find_package_multi"] = "in"
        if self.options.with_icuio:
            self.cpp_info.components["icu-io"].names["cmake_find_package"] = "io"
            self.cpp_info.components["icu-io"].names["cmake_find_package_multi"] = "io"
        if self.settings.os != "Windows" and self.options.data_packaging in ["files", "archive"]:
            self.env_info.ICU_DATA.append(data_path)
        if self._enable_icu_tools:
            self.cpp_info.components["icu-tu"].names["cmake_find_package"] = "tu"
            self.cpp_info.components["icu-tu"].names["cmake_find_package_multi"] = "tu"
            self.cpp_info.components["icu-test"].names["cmake_find_package"] = "test"
            self.cpp_info.components["icu-test"].names["cmake_find_package_multi"] = "test"
        if self._enable_icu_tools or self.options.with_extras:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
