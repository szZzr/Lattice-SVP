CC = g++-10
AR = ar rcs
STD = c++17
INCLUDES = -I/usr/include \
	-I/usr/include/boost

LIBRARIES = -L/usr/lib/x86_64-linux-gnu/libboost_serialization.a \
	-L/usr/lib/x86_64-linux-gnu/libzmq.a

BUILD_PATH = ../libs
TARGET = $(BUILD_PATH)/libMyTool.a
OBJECTS = libUtils.o \
	libPair.o \
	libNode.o \
	libTree.o \
	libJobs.o \
	libJobsEstimator.o \
	libJobsPair.o \

all: $(TARGET)
	@echo All done

$(TARGET): $(OBJECTS)
	$(AR) $@ $^

lib%.o : %.cpp
	$(CC) -fPIC $(LIBRARIES) -lboost_serialization -lzmq -c -std=$(STD) $< -o $@

libTree.o : Tree.hpp
libNode.o : Node.hpp
libPair.o : Pair.hpp
libJobs.o : Jobs.hpp
libJobsEstimator.o : JobsEstimator.h
libJobsPair.o : JobsPair.h
libJobs_Utils.o: Utils.cpp

clean:
	rm -f $(OBJECTS) $(TARGET)
	@echo Clean done 
