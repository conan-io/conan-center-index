from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildToolchain
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class LibUSBConan(ConanFile):
    name = "libusb"
    description = "A cross-platform library to access USB devices"
    license = "LGPL-2.1"
    homepage = "https://github.com/libusb/libusb"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("usb", "device")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_udev": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_udev": True,
    }

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "Android"]:
            del self.options.enable_udev
        # FIXME: enable_udev should be True for Android, but libudev recipe is missing
        if self.settings.os == "Android":
            self.options.enable_udev = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os == "Linux":
            if self.options.enable_udev:
                self.requires("libudev/system")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = self._msbuild_configuration
            tc.properties["WholeProgramOptimization"] = "false"
            tc.generate()
        else:
            VirtualBuildEnv(self).generate()
            tc = AutotoolsToolchain(self)
            if self.settings.os in ["Linux", "Android"]:
                tc.configure_args.append("--enable-udev" if self.options.enable_udev else "--disable-udev")
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            solution_msvc_year = "2017" if Version(self.version) < "1.0.24" else "2019"
            solution = f"libusb_{'dll' if self.options.shared else 'static'}_{solution_msvc_year}.vcxproj"
            vcxproj_path = os.path.join(self.source_folder, "msvc", solution)

            #==============================
            # TODO: to remove once https://github.com/conan-io/conan/pull/12817 available in conan client
            replace_in_file(
                self, vcxproj_path,
                "<WholeProgramOptimization Condition=\"'$(Configuration)'=='Release'\">true</WholeProgramOptimization>",
                "",
            )
            old_toolset = "v141" if Version(self.version) < "1.0.24" else "v142"
            new_toolset = MSBuildToolchain(self).toolset
            replace_in_file(
                self, vcxproj_path,
                f"<PlatformToolset>{old_toolset}</PlatformToolset>",
                f"<PlatformToolset>{new_toolset}</PlatformToolset>",
            )
            conantoolchain_props = os.path.join(self.generators_folder, MSBuildToolchain.filename)
            replace_in_file(
                self, vcxproj_path,
                "<Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
                f"<Import Project=\"{conantoolchain_props}\" /><Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
            )
            #==============================

            msbuild = MSBuild(self)
            msbuild.build_type = self._msbuild_configuration
            msbuild.build(vcxproj_path)
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, "libusb.h", src=os.path.join(self.source_folder, "libusb"),
                                   dst=os.path.join(self.package_folder, "include", "libusb-1.0"))
            copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libusb-1.0")
        prefix = "lib" if is_msvc(self) else ""
        self.cpp_info.libs = [f"{prefix}usb-1.0"]
        self.cpp_info.includedirs.append(os.path.join("include", "libusb-1.0"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Macos":
            self.cpp_info.system_libs = ["objc"]
            self.cpp_info.frameworks = ["IOKit", "CoreFoundation", "Security"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32"]
