cmake_minimum_required(VERSION 3.2)
project(bytebuffer)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES
    bytebuffer.cc
    bytebuffer_unittest.cc)
#    byteorder_unittest.cc

add_executable(bytebuffer ${SOURCE_FILES})