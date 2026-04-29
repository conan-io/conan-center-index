#!/bin/sh
# cl wrapper (cc_basename=cl -> libtool MSVC mode)
# Translates -lfoo -> foo.lib, -Lpath -> -libpath:path, -Wl,f1,f2 -> f1 f2
# All linker flags (-l, -L, -Wl) are accumulated and placed after -link.
#
# $REAL_CC must be set to the actual compiler (cl.exe or clang-cl path).
# MUST use POSIX sh — MSYS2 /bin/sh is NOT bash (no arrays, no +=).
tmpf=$(mktemp)
trap 'rm -f "$tmpf"' EXIT
link_flags=""
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
            lib="${arg#-l}.lib"
            if [ "$had_link" = "1" ]; then
                echo "$lib" >> "$tmpf"
            else
                link_flags="$link_flags $lib"
            fi
            ;;
        -L*)
            lp="-libpath:${arg#-L}"
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
