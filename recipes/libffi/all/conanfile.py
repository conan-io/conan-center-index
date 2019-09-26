from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform
from contextlib import contextmanager


class LibffiConan(ConanFile):
    name = "libffi"
    version = "3.2.1"
    description = "A portable, high level programming interface to various calling conventions"
    topics = ("conan", "libffi")
    url = "https://github.com/bincrafters/conan-libffi"
    homepage = "https://sourceware.org/libffi/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    _source_subfolder = "sources"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_files(self):
        configure_path = os.path.join(self._source_subfolder, "configure")
        tools.replace_in_file(configure_path,
                              "LIBTOOL='$(SHELL) $(top_builddir)/libtool'\n",
                              "LIBTOOL='$(SHELL) $(top_builddir)/libtool.sh'\n")
        tools.replace_in_file(configure_path,
                              "ofile=libtool\n",
                              "ofile=libtool.sh\n")

        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "x86", "win64.S"),
                              "jmp\tSHORT",
                              "jmp")

        ffi_extern_src = "/* Need minimal decorations for DLLs to works on Windows. */\n" \
                         "/* GCC has autoimport and autoexport.  Rely on Libtool to */\n" \
                         "/* help MSVC export from a DLL, but always declare data   */\n" \
                         "/* to be imported for MSVC clients.  This costs an extra  */\n" \
                         "/* indirection for MSVC clients using the static version  */\n" \
                         "/* of the library, but don't worry about that.  Besides,  */\n" \
                         "/* as a workaround, they can define FFI_BUILDING if they  */\n" \
                         "/* *know* they are going to link with the static library. */\n" \
                         "#if defined _MSC_VER && !defined FFI_BUILDING\n" \
                         "#define FFI_EXTERN extern __declspec(dllimport)\n" \
                         "#else\n" \
                         "#define FFI_EXTERN extern\n" \
                         "#endif\n" \
                         "\n"
        ffi_extern_dst = "#if defined _MSC_VER\n" \
                         "#  if !defined FFI_STATIC\n" \
                         "#    if defined FFI_BUILDING\n" \
                         "#      define FFI_EXTERN __declspec(dllexport)\n" \
                         "#    else\n" \
                         "#      define FFI_EXTERN __declspec(dllimport)\n" \
                         "#    endif\n" \
                         "#  else\n" \
                         "#      define FFI_EXTERN extern\n" \
                         "#  endif\n" \
                         "#else\n" \
                         "#  define FFI_EXTERN extern\n" \
                         "#endif\n"

        ffi_h_in = os.path.join(self._source_subfolder, "include", "ffi.h.in")
        tools.replace_in_file(ffi_h_in, ffi_extern_src, "")
        tools.replace_in_file(ffi_h_in,
                              "#include <ffitarget.h>\n",
                              "#include <ffitarget.h>\n" \
                              "\n" \
                              "{}".format(ffi_extern_dst))

        functions = [
            "ffi_status ffi_prep_cif_core(",
            "void ffi_raw_call (",
            "void ffi_ptrarray_to_raw (",
            "void ffi_raw_to_ptrarray (",
            "size_t ffi_raw_size (",
            "void ffi_java_raw_call (",
            "void ffi_java_ptrarray_to_raw (",
            "void ffi_java_raw_to_ptrarray (",
            "size_t ffi_java_raw_size (",
            "void *ffi_closure_alloc (",
            "void ffi_closure_free (",
            "ffi_status\nffi_prep_closure (",
            "ffi_status\nffi_prep_closure_loc (",
            "ffi_status\nffi_prep_raw_closure (",
            "ffi_status\nffi_prep_raw_closure_loc (",
            "ffi_status\nffi_prep_java_raw_closure (",
            "ffi_status\nffi_prep_java_raw_closure_loc (",
            "ffi_status ffi_prep_cif(",
            "ffi_status ffi_prep_cif_var(",
            "void ffi_call(",
        ]

        for function in functions:
            tools.replace_in_file(ffi_h_in,
                                  function,
                                  "FFI_EXTERN {}".format(function))

        types_c_src = os.path.join(self._source_subfolder, "src", "types.c")
        tools.replace_in_file(types_c_src,
                              "#include <ffi_common.h>",
                              "#include <ffi_common.h>\n"
                              "\n"
                              "#include <complex.h>")
        tools.replace_in_file(types_c_src,
                              "FFI_COMPLEX_TYPEDEF(name, type, maybe_const)",
                              "FFI_COMPLEX_TYPEDEF(name, complex_type, maybe_const)")
        tools.replace_in_file(types_c_src,
                              "_Complex type",
                              "complex_type")
        tools.replace_in_file(types_c_src,
                              "#ifdef FFI_TARGET_HAS_COMPLEX_TYPE",
                              "#ifdef _MSC_VER"
                              "\n#  define FLOAT_COMPLEX _C_float_complex"
                              "\n#  define DOUBLE_COMPLEX _C_double_complex"
                              "\n#  define LDOUBLE_COMPLEX _C_ldouble_complex"
                              "\n#else"
                              "\n#  define FLOAT_COMPLEX float _Complex"
                              "\n#  define DOUBLE_COMPLEX double _Complex"
                              "\n#  define LDOUBLE_COMPLEX long double _Complex"
                              "\n#endif"
                              "\n"
                              "\n#ifdef FFI_TARGET_HAS_COMPLEX_TYPE")
        tools.replace_in_file(types_c_src,
                              "FFI_COMPLEX_TYPEDEF(float, float, const)",
                              "FFI_COMPLEX_TYPEDEF(float, FLOAT_COMPLEX, const)")
        tools.replace_in_file(types_c_src,
                              "FFI_COMPLEX_TYPEDEF(double, double, const)",
                              "FFI_COMPLEX_TYPEDEF(double, DOUBLE_COMPLEX, const)")
        tools.replace_in_file(types_c_src,
                              "FFI_COMPLEX_TYPEDEF(longdouble, long double, FFI_LDBL_CONST)",
                              "FFI_COMPLEX_TYPEDEF(longdouble, LDOUBLE_COMPLEX, FFI_LDBL_CONST)")
        if self.settings.os == "Macos":
            tools.replace_in_file(configure_path, r"-install_name \$rpath/", "-install_name ")

        if self.settings.compiler == "clang" and float(str(self.settings.compiler.version)) >= 7.0:
            # https://android.googlesource.com/platform/external/libffi/+/ca22c3cb49a8cca299828c5ffad6fcfa76fdfa77
            sysv_s_src = os.path.join(self._source_subfolder, "src", "arm", "sysv.S")
            tools.replace_in_file(sysv_s_src, "fldmiad", "vldmia")
            tools.replace_in_file(sysv_s_src, "fstmiad", "vstmia")
            tools.replace_in_file(sysv_s_src, "fstmfdd\tsp!,", "vpush")

            # https://android.googlesource.com/platform/external/libffi/+/7748bd0e4a8f7d7c67b2867a3afdd92420e95a9f
            tools.replace_in_file(sysv_s_src, "stmeqia", "stmiaeq")
                
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            if self.options.shared:
                del self.options.fPIC

    def configure(self):
        if self.settings.compiler != "Visual Studio":
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ:
            self.build_requires("msys2/20161025")

    def _get_auto_tools(self):
        return AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

    @contextmanager
    def _create_auto_tools_environment(self, autotools):
        extra_env_vars = {}
        if self.settings.compiler == "Visual Studio":
            self.package_folder = tools.unix_path(self.package_folder)
            msvcc = tools.unix_path(os.path.join(self.source_folder, self._source_subfolder, "msvcc.sh"))
            msvcc.replace("\\", "/")
            msvcc_args = []
            autotools.defines.append("FFI_BUILDING")
            if not self.options.shared:
                autotools.defines.append("FFI_STATIC")
            if "MT" in self.settings.compiler.runtime:
                autotools.defines.append("USE_STATIC_RTL")
            if "d" in self.settings.compiler.runtime:
                autotools.defines.append("USE_DEBUG_RTL")
            if self.settings.arch == "x86_64":
                msvcc_args.append("-m64")
            elif self.settings.arch == "x86":
                msvcc_args.append("-m32")
            if msvcc_args:
                msvcc = "{} {}".format(msvcc, " ".join(msvcc_args))
            extra_env_vars.update(tools.vcvars_dict(self.settings))
            extra_env_vars.update({
                "INSTALL": tools.unix_path(os.path.join(self.source_folder, self._source_subfolder, "install-sh")),
                "LIBTOOL": tools.unix_path(os.path.join(self.source_folder, self._source_subfolder, "ltmain.sh")),
                "CC": msvcc,
                "CXX": msvcc,
                "LD": "link",
                "CPP": "cl -nologo -EP",
                "CXXCPP": "cl -nologo -EP",
            })
        with tools.environment_append(extra_env_vars):
            yield

    def build(self):
        self._patch_files()
        config_args = [
            "--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug",
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--disable-static" if self.options.shared else "--enable-static",
        ]
        autotools = self._get_auto_tools()
        build = None
        host = None
        if self.settings.compiler == "Visual Studio":
            build = "{}-{}-{}".format(
                "x86_64" if "64" in platform.machine() else "i686",
                "pc" if self.settings.arch == "x86" else "w64",
                "cygwin")
            host = "{}-{}-{}".format(
                "x86_64" if self.settings.arch == "x86_64" else "i686",
                "pc" if self.settings.arch == "x86" else "w64",
                "cygwin")
        else:
            if autotools.host and "x86-" in autotools.host:
                autotools.host = autotools.host.replace("x86", "i686")
        with self._create_auto_tools_environment(autotools):
            autotools.configure(configure_dir=os.path.join(self.source_folder, self._source_subfolder),
                                build=build,
                                host=host,
                                args=config_args)
            autotools.make()
            if tools.get_env("CONAN_RUN_TESTS", False):
                autotools.make(target="check")

    def package(self):
        if self.settings.os == "Windows":
            self.copy("*.h", src="{}/include".format(self.build_folder), dst="include")
        if self.settings.compiler == "Visual Studio":
            self.copy("*.lib", src="{}/.libs".format(self.build_folder), dst="lib")
            self.copy("*.dll", src="{}/.libs".format(self.build_folder), dst="bin")
        else:
            autotools = self._get_auto_tools()
            with self._create_auto_tools_environment(autotools):
                with tools.chdir(self.build_folder):
                    autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        pc = os.path.join(self.package_folder, "lib", "libffi.la")
        if os.path.isfile(pc):
            os.unlink(pc)
        self.copy("LICENSE", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.includedirs = ["include"]
        else:
            self.cpp_info.includedirs = [os.path.join("lib", "{}-{}".format(self.name, self.version), "include")]
        libdirs = ["lib"]
        if not self.options.shared:
            self.cpp_info.defines += ["FFI_STATIC"]
        if os.path.exists(os.path.join(self.package_folder, "lib64")):
            libdirs.append("lib64")
        if os.path.exists(os.path.join(self.package_folder, "lib32")):
            libdirs.append("lib32")
        self.cpp_info.libdirs = libdirs
        self.cpp_info.libs = tools.collect_libs(self)
