newoption {
    trigger = "to",
    value   = "path",
    description = "Set the output location for the generated files"
}

solution "test_package_sln"
    configurations {
        "Debug",
        "Release",
    }

    platforms {
        "x32",
        "x64",
        "Native",
    }

    language "C++"

    location (_WORKING_DIR)

dofile "test_package.lua"
