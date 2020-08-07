IF (BUILD_EXAMPLES OR BUILD_TESTS)
  IF (EXISTS ${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    INCLUDE(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    CONAN_BASIC_SETUP()
  ELSE ()
    MESSAGE(FATAL_ERROR "The file conanbuildinfo.cmake doesn't exist, you have to run conan install first")
  ENDIF ()

  ADD_COMPILE_OPTIONS(-DFMT_HEADER_ONLY=1)
ENDIF ()

INCLUDE(CheckIncludeFileCXX)

CHECK_INCLUDE_FILE_CXX(stdint.h HAVE_STDINT_H)
CHECK_INCLUDE_FILE_CXX(string.h HAVE_STRING_H)
CHECK_INCLUDE_FILE_CXX(new HAVE_NEW)
CHECK_INCLUDE_FILE_CXX(typeindex HAVE_TYPEINDEX)
CHECK_INCLUDE_FILE_CXX(utility HAVE_UTILITY)

IF (BUILD_TESTS)
  IF (CMAKE_BUILD_TYPE STREQUAL "Debug")
    SET(GTEST_LIB gtest_maind gtestd)
  ELSE ()
    SET(GTEST_LIB gtest_main gtest)
  ENDIF ()

  MESSAGE(VERBOSE "Linking to gtest library: ${GTEST_LIB}")
  ENABLE_TESTING()
ENDIF ()

IF (WIN32)
  MESSAGE(AUTHOR_WARNING "Windows is NOT OFFICIALLY SUPPORTED for now")
  MESSAGE(AUTHOR_WARNING "Turn GEN_HEADER and ENABLE_COVERAGE off on Windows")
  MESSAGE(AUTHOR_WARNING "DO NOT REMOVE ${CMAKE_SOURCE_DIR}/include/kerfuffle.h")

  SET(GEN_HEADER OFF)
  SET(ENABLE_COVERAGE OFF)
ENDIF ()

INCLUDE(FindPython3)

IF (NOT Python3_FOUND)
  IF (GEN_HEADER)
    MESSAGE(FATAL_ERROR "require python3 to build project")
  ENDIF ()
ENDIF ()