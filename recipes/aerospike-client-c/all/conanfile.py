import os
import yaml

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0.0"


class AerospikeConan(ConanFile):
    name = "aerospike-client-c"
    homepage = "https://github.com/aerospike/aerospike-client-c"
    description = "The Aerospike C client provides a C interface for interacting with the Aerospike Database."
    topics = ("aerospike", "client", "database")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "event_library": ["libev", "libuv", "libevent", None]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "event_library": None,
    }

    exports = "submoduledata.yml"

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "This recipe is not compatible with Windows")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        self.requires("zlib/[>=1.2.11 <2]")

        # in the original code lua is used as a submodule.
        # when creating a new version, you need to manually check which version of lua is used in the submodule.
        if self.version == "6.6.0":
            self.requires("lua/5.4.6")
        elif self.version == "7.2.1":
            self.requires("lua/5.4.6")
            self.requires("libyaml/0.2.5")
        else:
            raise ConanException(f"unknow version of lua used in the {self.version} of aerospike-client-c")

        if self.options.event_library == "libev":
            self.requires("libev/[>=4.24 <5]")
        elif self.options.event_library == "libuv":
            self.requires("libuv/[>=1.15.0 <2]")
        elif self.options.event_library == "libevent":
            self.requires("libevent/[>=2.1.8 <3]")

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder='src')

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        submodule_filename = os.path.join(self.recipe_folder, 'submoduledata.yml')
        with open(submodule_filename, 'r') as submodule_stream:
            submodules_data = yaml.safe_load(submodule_stream)
            for path, submodule in submodules_data["submodules"][self.version].items():
                archive_name = os.path.splitext(
                    os.path.basename(submodule["url"]))[0]
                get(self, url=submodule["url"],
                    sha256=submodule["sha256"],
                    destination=path,
                    filename=archive_name,
                    strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        includes = []
        for _, dependency in self.dependencies.items():
            for path in dependency.cpp_info.includedirs:
                includes.append(path)

        lua_include = self.dependencies["lua"].cpp_info.includedirs[0]
        event_library = ""
        if self.options.event_library:
            event_library = f"EVENT_LIB={self.options.event_library}"
        include_flags = ' '.join([f'-I{i}' for i in includes])

        ld_flags = ""
        if self.options.shared:
            libs = []
            for _, dependency in self.dependencies.items():
                for dir in dependency.cpp_info.libdirs:
                    for lib in os.listdir(dir):
                        if lib.endswith(".a"):
                            libs.append(os.path.join(dir, lib))
            libs_str = " ".join(libs)
            ld_flags = f"LDFLAGS='{libs_str}'"

        self.run(
            f"make TARGET_BASE='target' {event_library} {ld_flags} LUAMOD='{lua_include}' EXT_CFLAGS='{include_flags}' -C {self.source_path}")

    def package(self):
        if self.options.shared:
            copy(self, src=f"{self.source_folder}/target", pattern="lib/*.so*", dst=self.package_folder)
            copy(self, src=f"{self.source_folder}/target", pattern="lib/*.dylib", dst=self.package_folder)
        else:
            copy(self, src=f"{self.source_folder}/target", pattern="lib/*.a", dst=self.package_folder)

        copy(self, pattern="*",
             src=f'{self.source_folder}/src/include', dst=f'{self.package_folder}/include')
        copy(self, pattern="*",
             src=f'{self.source_folder}/modules/common/src/include', dst=f'{self.package_folder}/include')
        copy(self, pattern="LICENSE.md", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["aerospike"]

        self.cpp_info.defines = []
        if self.options.event_library == "libev":
            self.cpp_info.defines.append("AS_USE_LIBEV")
        elif self.options.event_library == "libuv":
            self.cpp_info.defines.append("AS_USE_LIBUV")
        elif self.options.event_library == "libevent":
            self.cpp_info.defines.append("AS_USE_LIBEVENT")
