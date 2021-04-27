//
//  Pair.hpp
//  pythonic
//
//  Created by Giorgos Rizos on 2/2/21.
//  Copyright © 2021 Giorgos Rizos. All rights reserved.
//

#ifndef Pair_hpp
#define Pair_hpp
#include "Utils.cpp"

template<class T>
class Pair{
public:
    int limit;
    size_t length, pos; //pos: declares the position of pointer
    T* job;

    Pair();
    Pair(int limit, size_t length, T j);
    Pair(int limit, size_t length, T* job);
    Pair(int limit, size_t length, T* job, size_t pos);
    Pair<T> operator=(Pair<T> p);

    T* get_job();

    void show();
    std::string display();
    void show_(char *str);
    Pair<T> tempo(int t);
    
    ///SERIALIZATION
    template<class Archive>
    void save(Archive & ar, const unsigned int version) const;
    template<class Archive>
    void load(Archive & ar, const unsigned int version) ;
    BOOST_SERIALIZATION_SPLIT_MEMBER()
    
    void deserialize(char *str);
    
};


///SERIALIZATION
template<class T>
template<class Archive>
void Pair<T>::save(Archive & ar, const unsigned int version) const{
    ar << limit;
    ar << length;
    for(int i=0; i<length;i++){
        std::cout<<job[i]<<" - ";
        ar << job[i];
    }
    std::cout<<"\n";
    ar << pos;
}

template<class T>
template<class Archive>
void Pair<T>::load(Archive & ar, const unsigned int version){
    ar >> limit;
    ar >> length;
    job = new T[length]();
    for(int i=0; i<length;i++){
        ar >> job[i];
        std::cout<<job[i]<<" - ";
    }
    std::cout<<"\n";
    ar >> pos;
}


#endif /* Pair_hpp */

