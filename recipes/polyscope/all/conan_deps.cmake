if(POLYSCOPE_BACKEND_OPENGL3_GLFW)
    find_package(glfw3 REQUIRED CONFIG)
    list(APPEND BACKEND_SRCS "${CMAKE_CURRENT_LIST_DIR}/include/backends/imgui_impl_glfw.cpp")
endif()

if(POLYSCOPE_BACKEND_OPENGL3_GLFW OR POLYSCOPE_BACKEND_OPENGL3_EGL)
    find_package(glad REQUIRED CONFIG)
    list(APPEND BACKEND_SRCS "${CMAKE_CURRENT_LIST_DIR}/include/backends/imgui_impl_opengl3.cpp")
endif()

find_package(glm REQUIRED CONFIG)
find_package(imgui REQUIRED CONFIG)
find_package(nlohmann_json REQUIRED CONFIG)
