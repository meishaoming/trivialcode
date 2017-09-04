cmake_minimum_required(VERSION 3.7)
project(des)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES
        des.c
        des.h main.c)

add_executable(des ${SOURCE_FILES})