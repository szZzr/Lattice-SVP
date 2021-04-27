cmake_minimum_required(VERSION 3.17)
project(pythonic)

set(CMAKE_CXX_STANDARD 17)

# see https://cmake.org/cmake/help/latest/module/FindBoost.html
find_package(Boost REQUIRED)

include_directories(${Boost_INCLUDE_DIR})

INCLUDE_DIRECTORIES( /usr/local/Cellar/zeromq/4.3.2/include )
INCLUDE_DIRECTORIES( /usr/local/Cellar/boost/1.72.0_1/include )
LINK_DIRECTORIES( /usr/local/Cellar/zeromq/4.3.2/lib )
LINK_DIRECTORIES( /usr/local/Cellar/boost/1.72.0_1/lib )

include_directories(${PROJECT_SOURCE_DIR})

add_executable(pythonic main.cpp Pair.cpp Node.cpp Tree.cpp Jobs.cpp JobsEstimator.cpp JobsEstimator.h)

TARGET_LINK_LIBRARIES( pythonic LINK_PUBLIC ${Boost_LIBRARIES} )
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -lboost_serialization" )