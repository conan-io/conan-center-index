--- CMakeLists.txt
+++ CMakeLists.txt
@@ -98,7 +98,7 @@
     target_compile_definitions(aws-checksums PRIVATE "-DDEBUG_BUILD")
 endif()

-target_include_directories(${CMAKE_PROJECT_NAME} PUBLIC
+target_include_directories(${PROJECT_NAME} PUBLIC
     $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
     $<INSTALL_INTERFACE:include>)

@@ -129,7 +129,7 @@
 endif()

 install(FILES ${AWS_CHECKSUMS_HEADERS} DESTINATION "include/aws/checksums")
-aws_prepare_shared_lib_exports(${CMAKE_PROJECT_NAME})
+aws_prepare_shared_lib_exports(${PROJECT_NAME})

 if (BUILD_SHARED_LIBS)
    set (TARGET_DIR "shared")
@@ -137,14 +137,14 @@
    set (TARGET_DIR "static")
 endif()

-install(EXPORT "${CMAKE_PROJECT_NAME}-targets"
-    DESTINATION "${LIBRARY_DIRECTORY}/${CMAKE_PROJECT_NAME}/cmake/${TARGET_DIR}/"
+install(EXPORT "${PROJECT_NAME}-targets"
+    DESTINATION "${LIBRARY_DIRECTORY}/${PROJECT_NAME}/cmake/${TARGET_DIR}/"
     NAMESPACE AWS::)

-configure_file("cmake/${CMAKE_PROJECT_NAME}-config.cmake"
-    "${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}-config.cmake"
+configure_file("cmake/${PROJECT_NAME}-config.cmake"
+    "${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-config.cmake"
     @ONLY)

-install(FILES "${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}-config.cmake"
-    DESTINATION "${LIBRARY_DIRECTORY}/${CMAKE_PROJECT_NAME}/cmake/")
+install(FILES "${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-config.cmake"
+    DESTINATION "${LIBRARY_DIRECTORY}/${PROJECT_NAME}/cmake/")

