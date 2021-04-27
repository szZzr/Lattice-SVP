CC = g++
AR = ar rcs
STD = c++17
INCLUDES = -I/usr/local/Cellar/zeromq/4.3.2/include \
	-I/usr/local/Cellar/boost/1.72.0_1/include

BUILD_PATH = ../bin2
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
	$(CC) $(INCLUDES) -c -std=$(STD) $< -o $@

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
