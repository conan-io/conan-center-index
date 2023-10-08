if(ARROW_S3)
  find_package(AWSSDK REQUIRED)
  # Fix issue where scripts expect a variable called "AWSSDK_LINK_LIBRARIES"
  # which is not defined by the generated AWSSDKConfig.cmake
  set(AWSSDK_LINK_LIBRARIES "${AWSSDK_LIBRARIES}")

  # Avoid logic related to generating a .pc file
  set(AWSSDK_SOURCE "conan")
endif()