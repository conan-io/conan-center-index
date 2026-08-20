#!/bin/sh
# cl wrapper (cc_basename=cl -> libtool MSVC mode)
# Translates -lfoo -> foo.lib, -Lpath -> -libpath:path, -Wl,f1,f2 -> f1 f2
# All linker flags (-l, -L, -Wl) are accumulated and placed after -link.
#
# For -lfoo, the wrapper searches known -L directories for the actual library file (foo.lib, libfoo.a, libfoo.lib, foo.a)
# to handle non-MSVC naming (e.g. Meson produces libfoo.a on Windows even with MSVC/clang-cl).
# Falls back to foo.lib if no file is found.
#
# $REAL_CC must be set to the actual compiler (cl.exe or clang-cl path).
# MUST use POSIX sh — MSYS2 /bin/sh is NOT bash (no arrays, no +=).

# resolve_lib NAME: search lib_dirs for the actual library file matching NAME.
# Prints the resolved filename (e.g. lcms2.lib or liblcms2.a).
# Falls back to NAME.lib if not found in any directory.
resolve_lib() {
    _name="$1"
    for _dir in $lib_dirs; do
        for _candidate in "${_name}.lib" "lib${_name}.a" "lib${_name}.lib" "${_name}.a"; do
            if [ -f "${_dir}/${_candidate}" ]; then
                echo "$_candidate"
                return
            fi
        done
    done
    echo "${_name}.lib"
}

tmpf=$(mktemp)
trap 'rm -f "$tmpf"' EXIT
link_flags=""
lib_dirs=""
had_link=0
for arg; do
    case "$arg" in
        -link|-LINK|-link.exe)
            had_link=1
            echo "-link" >> "$tmpf"
            # Flush accumulated linker flags right after -link
            if [ -n "$link_flags" ]; then
                for lf in $link_flags; do echo "$lf" >> "$tmpf"; done
                link_flags=""
            fi
            ;;
        -LIBPATH:*|-libpath:*)
            # MSVC-native libpath — pass through unchanged.
            # Must be matched BEFORE -l* / -L* because MSYS2 sh case-folds paths: -LIBPATH: would match -L*.
            echo "$arg" >> "$tmpf"
            ;;
        -Wl,*)
            # GCC-style linker passthrough: -Wl,flag1,flag2 -> flag1 flag2
            # cl.exe does not understand -Wl, but we can translate it.
            rest="${arg#-Wl,}"
            old_IFS="$IFS"; IFS=','
            for wl_flag in $rest; do
                if [ "$had_link" = "1" ]; then
                    echo "$wl_flag" >> "$tmpf"
                else
                    link_flags="$link_flags $wl_flag"
                fi
            done
            IFS="$old_IFS"
            ;;
        -l*)
            lib=$(resolve_lib "${arg#-l}")
            if [ "$had_link" = "1" ]; then
                echo "$lib" >> "$tmpf"
            else
                link_flags="$link_flags $lib"
            fi
            ;;
        -L*)
            dir="${arg#-L}"
            lib_dirs="$lib_dirs $dir"
            lp="-libpath:$dir"
            if [ "$had_link" = "1" ]; then
                echo "$lp" >> "$tmpf"
            else
                link_flags="$link_flags $lp"
            fi
            ;;
        *)  echo "$arg" >> "$tmpf" ;;
    esac
done
# Append remaining linker flags after -link
if [ -n "$link_flags" ]; then
    echo "-link" >> "$tmpf"
    for lf in $link_flags; do echo "$lf" >> "$tmpf"; done
fi
# Read back args, one per line, and exec the real compiler
set --
while IFS= read -r line; do
    set -- "$@" "$line"
done < "$tmpf"
exec "$REAL_CC" "$@"
