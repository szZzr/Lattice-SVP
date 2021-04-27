//
//  Jobs_Utils.cpp
//  pythonic
//
//  Created by Giorgos Rizos on 24/1/21.
//  Copyright © 2021 Giorgos Rizos. All rights reserved.
//

#include <stdio.h>
#include <string>
#include <cstring>
#include <zmq.hpp>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>
#include <boost/serialization/string.hpp>
#include <boost/serialization/utility.hpp>
#include <boost/serialization/serialization.hpp>
#include <boost/serialization/split_member.hpp>
#include <iostream>


template<class T>
//std::string serialization(T object){
char * serialization(T object){
    std::ostringstream ss;
    boost::archive::text_oarchive oa(ss);
    oa<<object;
    std::string archive_str = ss.str();
    
    char * buffer = new char [archive_str.length() + 1];
    strcpy(buffer, archive_str.c_str());
    return buffer;
    
//    return archive_str;
}

template<class T>
void serialization(T object, char* & str){
    std::ostringstream ss;
    boost::archive::text_oarchive oa(ss);
    oa<<object;
    std::string archive_str = ss.str();
    
    str = new char [archive_str.length() + 1];
    strcpy(str, archive_str.c_str());
    
    
}


template<class T>
T deserialization(std::string str){
    
    T object;
    std::istringstream iss(str);
    boost::archive::text_iarchive ia(iss);
    
    ia>>object;
    
    return object;
}

template<class T>
T deserialization(char * str){
    T object;
    std::string smessage(str);
    std::istringstream iss(smessage);
    boost::archive::text_iarchive ia(iss);

    ia>>object;
    return object;
}
