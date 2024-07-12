from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, export_conandata_patches, apply_conandata_patches, rm, unzip
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class OhPipelineConan(ConanFile):
    name = "ohpipeline"
    description = "OpenHome audio pipeline"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openhome/ohPipeline"
    topics = ("openhome", "ohnet", "ohpipeline", "upnp")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def export_sources(self):
        export_conandata_patches(self)

    def build_requirements(self):
        self.tool_requires("waf/[>=2.0.19]")
        self.tool_requires("cpython/[>=3.0.0]")

    def requirements(self):
        self.requires("ohnet/[>=1.36.5182]", transitive_headers=True, transitive_libs=True)
        self.requires("openssl/[>=1.1 <4]")
        self.requires("libmad/[>=0.15.1b]")
        self.requires("alac/[>=cci.20121212]")
        self.requires("libfdk_aac/[>=2.0.3]")
        self.requires("faac/[>=1.30]")
        self.requires("flac/[>=1.4.3]")
        self.requires("ogg/[>=1.3.5]")
        self.requires("vorbis/[>=1.3.7]")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["helpers"], destination='dependencies/AnyPlatform/ohWafHelpers', strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            self.run(f"LDFLAGS=-L{self.dependencies['zlib'].cpp_info.libdirs[0]} waf configure --ohnet-include-dir={self.dependencies['ohnet'].cpp_info.includedirs[0]} --ohnet-lib-dir={self.dependencies['ohnet'].cpp_info.libdirs[0]} --ohnet={self.dependencies['ohnet'].cpp_info.libdirs[0]}/.. --ssl={self.dependencies['openssl'].cpp_info.libdirs[0]}/.. --with-default-fpm")
            self.run("waf build")

    def package(self):
        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            self.run("waf bundle")
            unzip(self, "build/ohMediaPlayer.tar.gz", self.package_folder, strip_root=True)
            rm(self, "dependencies.json", self.package_folder)

    def package_info(self):
        self.cpp_info.libs = [
            'ohPipeline',
            'ohMediaPlayer',
            'ohMediaPlayerTestUtils',
            'SourcePlaylist',
            'SourceRadio',
            'SourceSongcast',
            'SourceRaop',
            'SourceScd',
            'SourceUpnpAv',
            'CodecAacFdk',
            'CodecAacFdkAdts',
            'CodecAacFdkBase',
            'CodecAacFdkMp4',
            'CodecAifc',
            'CodecAiff',
            'CodecAiffBase',
            'CodecAlacAppleBase',
            'CodecAlacApple',
            'CodecDsdDsf',
            'CodecDsdDff',
            'CodecDsdRaw',
            'CodecFlac',
            'CodecMp3',
            'CodecVorbis',
            'CodecWav',
            'CodecPcm',
            'libOgg',
            'WebAppFramework',
            'ConfigUi',
            'ConfigUiTestUtils',
            'Odp',
            'Podcast'
        ]
