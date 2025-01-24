from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeDeps, CMakeToolchain, CMake, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, download, export_conandata_patches, apply_conandata_patches
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
        self.tool_requires("cmake/[>3.23 <4]")

    def requirements(self):
        self.requires("ohnet/1.37.5454", transitive_headers=True, transitive_libs=True)
        self.requires("openssl/[>=1.1 <4]")
        self.requires("libmad/0.15.1b")
        self.requires("alac/cci.20121212")
        self.requires("libfdk_aac/2.0.3")
        self.requires("faac/1.30")
        self.requires("flac/1.4.3")
        self.requires("ogg/1.3.5")
        self.requires("vorbis/1.3.7")

    def layout(self):
        cmake_layout(self, src_folder="src")

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
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)
        download(self, **self.conan_data["sources"][self.version]["cmake"], filename="CMakeLists.txt")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = [
            "ohPipeline",
            "ohMediaPlayer",
            "Odp",
            "SourcePlaylist",
            "SourceRadio",
            "SourceSongcast",
            "SourceScd",
            "SourceRaop",
            "SourceUpnpAv",
            "Podcast",
            "ScdSender",
            "CodecWav",
            "CodecPcm",
            "CodecDsdDsf",
            "CodecDsdDff",
            "CodecDsdRaw",
            "CodecAiffBase",
            "CodecAifc",
            "CodecAiff",
            "CodecFlac",
            "CodecAlacAppleBase",
            "CodecAlacApple",
            "CodecAacFdkBase",
            "CodecAacFdkMp4",
            "CodecAacFdkAdts",
            "CodecMp3",
            "CodecVorbis",
            "WebAppFramework",
            "WebAppFrameworkTestUtils",
            "ConfigUi",
            "ConfigUiTestUtils",
        ]
