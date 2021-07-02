project "test_package"
    targetname "test_package"
    language "C++"
    kind "ConsoleApp"
    files {
        "../test_package.cpp",
    }
    location (_WORKING_DIR)
