from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get
from conan.errors import ConanInvalidConfiguration


class LelyConan(ConanFile):
    name = "lely"

    # Optional metadata
    license = "Apache"
    url = "https://gitlab.com/lely_industries/lely-core/"
    description = "<Description of LelyCore here>"
    topics = ("canopen",)

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "rt": [True, False],
        "threads": [True, False],
        "ecss-compliance": [True, False],
        "errno": [True, False],
        "malloc": [True, False],
        "stdio": [True, False],
        "cxx": [True, False],
        "daemon": [True, False],
        "diag": [True, False],
        "canfd": [True, False],
        "dcf": [True, False],
        "dcf-restore": [True, False],
        "obj-default": [True, False],
        "obj-file": [True, False],
        "obj-limits": [True, False],
        "obj-name": [True, False],
        "obj-upload": [True, False],
        "sdev": [True, False],
        "csdo": [True, False],
        "rpdo": [True, False],
        "tpdo": [True, False],
        "mpdo": [True, False],
        "sync": [True, False],
        "time": [True, False],
        "emcy": [True, False],
        "lss": [True, False],
        "wtm": [True, False],
        "master": [True, False],
        "ng": [True, False],
        "nmt-boot": [True, False],
        "nmt-cfg": [True, False],
        "gw": [True, False],
        "gw-txt": [True, False],
        "coapp-master": [True, False],
        "coapp-slave": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "rt": True,
        "threads": True,
        "ecss-compliance": False,
        "errno": True,
        "malloc": True,
        "stdio": True,
        "cxx": True,
        "daemon": True,
        "diag": True,
        "canfd": True,
        "dcf": True,
        "dcf-restore": True,
        "obj-default": True,
        "obj-file": True,
        "obj-limits": True,
        "obj-name": True,
        "obj-upload": True,
        "sdev": True,
        "csdo": True,
        "rpdo": True,
        "tpdo": True,
        "mpdo": True,
        "sync": True,
        "time": True,
        "emcy": True,
        "lss": True,
        "wtm": True,
        "master": True,
        "ng": True,
        "nmt-boot": True,
        "nmt-cfg": True,
        "gw": True,
        "gw-txt": True,
        "coapp-master": True,
        "coapp-slave": True,
    }

    def export_sources(self):
        export_conandata_patches(self)
        # return "configure.ac", "src/*", "include/*"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        # Windows requires proprietary from https://www.ixxat.com/technical-support/support/windows-driver-software
        # hence support for it will be skipped for now
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "This Conan version of this package is only compatible with Linux"
            )

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True,
        )

    def layout(self):
        basic_layout(self)

    def generate(self):
        at_toolchain = AutotoolsToolchain(self)
        at_toolchain.generate()

    def build(self):
        args = [
            "--disable-cython",
            "--disable-python",
            "--disable-tools",
            "--disable-dependency-tracking",
            "--disable-maintainer-mode",
        ]
        if self.options.get_safe("ecss-compliance"):
            args.append("--enable-ecss-compliance")
        disable_options = {
            "threads",
            "rt",
            "errno",
            "malloc",
            "stdio",
            "cxx",
            "daemon",
            "diag",
            "canfd",
            "dcf",
            "dcf-restore",
            "obj-default",
            "obj-file",
            "obj-limits",
            "obj-name",
            "obj-upload",
            "sdev",
            "csdo",
            "rpdo",
            "tpdo",
            "mpdo",
            "sync",
            "time",
            "emcy",
            "lss",
            "wtm",
            "master",
            "ng",
            "nmt-boot",
            "nmt-cfg",
            "gw",
            "gw-txt",
            "coapp-master",
            "coapp-slave",
        }
        for option in disable_options:
            if self.options.get_safe(option) == False:
                args.append(f"--disable-{option}")

        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure(args=args)
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        components = {
            "can": ["libc", "util"],
            "co": ["libc", "util", "can"],
            "coapp": ["libc", "io2", "co"],
            "ev": ["libc", "util"],
            "io2": ["libc", "util", "can", "ev"],
            "libc": [],
            "tap": ["libc"],
            "util": ["libc"],
        }
        for component, dependencies in components.items():
            self.cpp_info.components[component].libs = [f"lely-{component}"]
            self.cpp_info.components[component].requires = dependencies
