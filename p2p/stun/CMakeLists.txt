cmake_minimum_required(VERSION 3.6)
project(stun)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES main.c stun.c)
add_executable(stun ${SOURCE_FILES})