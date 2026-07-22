cmake_minimum_required(VERSION 3.20)
project(neuroforge_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(neuroforge INTERFACE)
target_include_directories(neuroforge INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)

if(MSVC)
    target_compile_options(neuroforge INTERFACE /W4 /permissive-)
else()
    target_compile_options(neuroforge INTERFACE -Wall -Wextra -Wpedantic -Wconversion)
endif()

add_executable(neuroforge_demo src/main.cpp)
target_link_libraries(neuroforge_demo PRIVATE neuroforge)

include(CTest)
if(BUILD_TESTING)
    add_executable(neuroforge_tests tests/test_autograd.cpp)
    target_link_libraries(neuroforge_tests PRIVATE neuroforge)
    add_test(NAME autograd COMMAND neuroforge_tests)
endif()
