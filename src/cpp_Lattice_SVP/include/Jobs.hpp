//
//  Jobs.hpp
//  DistNetwSystems
//
//  Created by Giorgos Rizos on 23/1/21.
//  Copyright © 2021 Giorgos Rizos. All rights reserved.
//

#ifndef Jobs_hpp
#define Jobs_hpp
#include <vector>
#include <math.h>

#include "Pair.hpp"


enum class Condition {VIA_NODES, VIA_DEPTH};

template<class T>
class Jobs{
public:
    Jobs();
    Jobs(std::size_t size_job);
    virtual void set_jobs();
    virtual void set_parameters(int range, std::size_t size_jobs);
    void show_array(T* arr, std::size_t size);
    void show_array2d(T* arr, std::size_t size);
//    std::vector< std::pair<T*,int> > get_jobs();
    void show();
    
    ///GETTERS
    std::size_t get_size_job() const;
    std::size_t get_size_jobs() const;
    int get_range() const;
    int get_step() const;
    
    ///OPERATIONAL
    char* next_pair();
    Jobs<T> operator=(Jobs<T> j);
    
    
    ///SERIALIZATION
    template<class Archive>
    void save(Archive & ar, const unsigned int version) const;
    template<class Archive>
    void load(Archive & ar, const unsigned int version) ;
    BOOST_SERIALIZATION_SPLIT_MEMBER()
    
    char* serialize(Jobs<T> jobs);
    std::string serialize(Jobs<T> jobs, bool _str);
    void serialize(char* &str);
    
//    Jobs<T> deserialize(char* str);
    void deserialize(std::string str);
    void deserialize(char* str);
    
    
protected:
    int range, step;
    static int iter;
    std::size_t size_job;
    std::size_t size_jobs;
//    std::vector< std::pair<T*,int> > jobs;
    std::vector< Pair<T> > jobs;
    

};

template<class T>
int Jobs<T>::iter = 0;


///SERIALIZATION
template<class T>
template<class Archive>
void Jobs<T>::save(Archive & ar, const unsigned int version) const{
    ar<<this->get_size_job();
    ar<<this->get_size_jobs();
    ar<<this->get_range();
    ar<<this->get_step();
    
    for(Pair<T> p: jobs){
        ar<<p;
    }
//    typedef std::pair<T*,int> t_pair;
//    for( t_pair p: jobs){
//
//        ar<<p.first[0];
//        ar<<p.second;
////        for(int i=0; i<size_job;i++){
////            ar<<p.first[i];
////        }
//    }
    
    
}

template<class T>
template<class Archive>
void Jobs<T>::load(Archive & ar, const unsigned int version) {
    ar>>this->size_job;
    ar>>this->size_jobs;
    ar>>this->range;
    ar>>this->step;
    
    for(int i=0; i<size_jobs;i++){
        Pair<T> p;
        ar>>p;
        jobs.push_back(p);
    }
    
//    int limit=0;
//    for(int p=0; p<size_jobs; p++){
//
//        T *job = new T[size_job]();
//        ar>>this->job[0];
//        ar>>this->limit;
////        for(int i=0; i<size_job; i++){
////            arr>>job[i];
////        }
//        jobs.push_back(std::make_pair((T*) job,(int) limit));
//    }
    
}
#endif /* Jobs_hpp */
