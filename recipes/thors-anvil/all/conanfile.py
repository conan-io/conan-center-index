from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.scm import Git
import os


required_conan_version = ">=2.0"


class ThorsAnvilConan(ConanFile):
    name = "thors-anvil"
    description = "C++20 monorepo: declarative serialization (JSON/YAML/BSON), async IO, coroutine HTTP server, MongoDB client, and hot-loadable plugin framework"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Loki-Astari/ThorsAnvil"
    topics = ("serialization", "json", "yaml", "bson", "mongodb", "http", "async", "coroutines")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("bzip2/1.0.8")
        self.requires("zlib/1.3.1")
        self.requires("libyaml/0.2.5")
        self.requires("snappy/1.2.1")
        self.requires("openssl/[>=3.0 <4]")
        self.requires("magic_enum/0.9.7")
        self.requires("boost/[>=1.70]")
        self.requires("libevent/2.1.12")

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/Loki-Astari/ThorsAnvil.git", target=".")
        git.checkout(commit=f"tags/{self.version}")
        git.run("submodule update --init --recursive")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--enable-test-with-conan",
            "--enable-dark-mode",
            "--disable-vera",
            "--disable-test-with-integration",
            "--disable-test-with-mongo-query",
            "--disable-Mongo-Service",
            "--disable-slacktest",
            f"--with-zlib-root={self.dependencies['zlib'].package_folder}",
            f"--with-yaml-root={self.dependencies['libyaml'].package_folder}",
            f"--with-snappy-root={self.dependencies['snappy'].package_folder}",
            f"--with-crypto-root={self.dependencies['openssl'].package_folder}",
            f"--with-magicenum-header-only-root={self.dependencies['magic_enum'].package_folder}/include",
            f"--with-event-root={self.dependencies['libevent'].package_folder}",
            "--with-custom-event=event_core",
        ])
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure(args=[f"--prefix={self.package_folder}"])
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install(args=[f"DESTDIR="])
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        suffix = "D" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [
            f"NisseBolt{suffix}",
            f"Nisse{suffix}",
            f"ThorsMongo{suffix}",
            f"ThorsSocket{suffix}",
            f"ThorsStorage{suffix}",
            f"ThorSerialize{suffix}",
            f"ThorsLogging{suffix}",
        ]
        self.cpp_info.includedirs = [
            "include",
            "include/ThorSerialize",
            "include/ThorsCrypto",
            "include/ThorsLogging",
            "include/ThorsMongo",
            "include/ThorsSocket",
            "include/ThorsStorage",
            "include/NisseBolt",
            "include/NisseHTTP",
            "include/NisseServer",
            "include/ThorsMug",
            "include/ThorsSlack",
            "include/fast_float",
        ]
