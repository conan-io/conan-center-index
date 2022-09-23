from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, load, replace_in_file, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, unix_path, VCVars
import os
import re
import shutil

required_conan_version = ">=1.52.0"


class LibjpegConan(ConanFile):
    name = "libjpeg"
    description = "Libjpeg is a widely used C library for reading and writing JPEG image files."
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("image", "format", "jpg", "jpeg", "picture", "multimedia", "graphics")
    license = "IJG"
    homepage = "http://ijg.org"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        copy(self, "Win32.Mak", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not (is_msvc(self) or self. _is_clang_cl) and \
           not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        if is_msvc(self) or self._is_clang_cl:
            vc = VCVars(self)
            vc.generate()
            env = Environment()
            env.define("PROFILE", None)
            env.define("TUNE", None)
            env.define("NODEBUG", None)
            env.vars(self).save_script("conanbuildenv_nmake")
        else:
            tc = AutotoolsToolchain(self)
            tc.extra_defines.append("LIBJPEG_BUILDING")
            tc.generate()
            env = VirtualBuildEnv(self)
            env.generate()

    def _build_nmake(self):
        copy(self, "Win32.Mak", src=os.path.join(self.source_folder, os.pardir), dst=self.source_folder)
        with chdir(self, self.source_folder):
            # export symbols if shared
            replace_in_file(
                self,
                "Win32.Mak",
                "\nccommon = -c ",
                "\nccommon = -c -DLIBJPEG_BUILDING {}".format("" if self.options.shared else "-DLIBJPEG_STATIC "),
            )
            # clean environment variables that might affect on the build (e.g. if set by Jenkins)
            shutil.copy("jconfig.vc", "jconfig.h")
            make_args = [
                "nodebug=1" if self.settings.build_type != "Debug" else "",
            ]
            if self._is_clang_cl:
                cl = os.environ.get("CC", "clang-cl")
                link = os.environ.get("LD", "lld-link")
                lib = os.environ.get("AR", "llvm-lib")
                rc = os.environ.get("RC", "llvm-rc")
                replace_in_file(self, "Win32.Mak", "cc     = cl", f"cc     = {cl}")
                replace_in_file(self, "Win32.Mak", "link   = link", f"link   = {link}")
                replace_in_file(self, "Win32.Mak", "implib = lib", f"implib = {lib}")
                replace_in_file(self, "Win32.Mak", "rc     = Rc", f"rc     = {rc}")
            # set flags directly in makefile.vc
            # cflags are critical for the library. ldflags and ldlibs are only for binaries
            if is_msvc_static_runtime(self):
                replace_in_file(self, "makefile.vc", "(cvars)", "(cvarsmt)")
                replace_in_file(self, "makefile.vc", "(conlibs)", "(conlibsmt)")
            else:
                replace_in_file(self, "makefile.vc", "(cvars)", "(cvarsdll)")
                replace_in_file(self, "makefile.vc", "(conlibs)", "(conlibsdll)")
            target = "{}/libjpeg.lib".format("shared" if self.options.shared else "static")
            self.run("nmake -f makefile.vc {} {}".format(" ".join(make_args), target))

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self) or self._is_clang_cl:
            self._build_nmake()
        else:
            autotools = Autotools(self)
            self.win_bash = True
            autotools.configure()
            autotools.make()
            self.win_bash = None

    def package(self):
        copy(self, "README", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self) or self._is_clang_cl:
            for filename in ["jpeglib.h", "jerror.h", "jconfig.h", "jmorecfg.h"]:
                copy(self, filename, src=self.source_folder, dst=os.path.join(self.package_folder, "include"), keep_path=False)

            copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            if self.options.shared:
                copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            autotools = Autotools(self)
            self.win_bash = True
            # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
            autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
            self.win_bash = None
            if self.settings.os == "Windows" and self.options.shared:
                rm(self, "*[!.dll]", os.path.join(self.package_folder, "bin"))
            else:
                rmdir(self, os.path.join(self.package_folder, "bin"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            fix_apple_shared_install_name(self)

        for fn in ("jpegint.h", "transupp.h",):
            copy(self, fn, src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

        for fn in ("jinclude.h", "transupp.c",):
            copy(self, fn, src=self.source_folder, dst=os.path.join(self.package_folder, "res"))

        # Remove export decorations of transupp symbols
        for relpath in os.path.join("include", "transupp.h"), os.path.join("res", "transupp.c"):
            path = os.path.join(self.package_folder, relpath)
            save(self, path, re.subn(r"(?:EXTERN|GLOBAL)\(([^)]+)\)", r"\1", load(self, path))[0])

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "JPEG")
        self.cpp_info.set_property("cmake_target_name", "JPEG::JPEG")
        self.cpp_info.set_property("pkg_config_name", "libjpeg")
        prefix = "lib" if is_msvc(self) or self._is_clang_cl else ""
        self.cpp_info.libs = [f"{prefix}jpeg"]
        if not self.options.shared:
            self.cpp_info.defines.append("LIBJPEG_STATIC")

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "JPEG"
        self.cpp_info.names["cmake_find_package_multi"] = "JPEG"
