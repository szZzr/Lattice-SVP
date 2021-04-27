//
//  Jobs.cpp
//  DistNetwSystems
//
//  Created by Giorgos Rizos on 23/1/21.
//  Copyright © 2021 Giorgos Rizos. All rights reserved.
//

#include "Jobs.hpp"

template<class T>
Jobs<T>::Jobs(){
    this->range = 0;
    this->step = 0;
    this->size_job = 0;
    this->size_jobs= 0;
}


template<class T>
Jobs<T>::Jobs(std::size_t size_job){
    this->range = 0;
    this->step = 0;
    this->size_job = size_job;
}


/// GETTERS
template<class T>
std::size_t Jobs<T>::get_size_job() const{
    return this->size_job;
}

template<class T>
std::size_t Jobs<T>::get_size_jobs() const{
    return this->size_jobs;
}

template<class T>
int Jobs<T>::get_range() const{
    return this->range;
}

template<class T>
int Jobs<T>::get_step() const{
    return this->step;
}

///INITIALIZATION
template<class T>
void Jobs<T>::set_parameters(int range, std::size_t size_jobs){
    this->range = range;
    this->size_jobs = (range<size_jobs) ? range : size_jobs;
    this->step = (int) ceil((this->range +1)/this->size_jobs);
}

template<class T>
void Jobs<T>::set_jobs(){
    int limit = 0, i;
    for(i=0; i<range; i+=step){
        limit=(i+step-1 > range) ? range : i + step -1;
        Pair<T> task(limit, size_job, i);
        jobs.push_back(task);
    }
    this->size_jobs = jobs.size();
    if(i==range){
        jobs[size_jobs-1].limit = i;
    }
}

template<class T>
void Jobs<T>::show(){
    std::cout<<"Show Vector\n"<<std::endl;
    for( Pair<T> p: jobs){
        std::cout<<p.display();
    }
}


///OPERATIONAL
template<class T>
char* Jobs<T>::next_pair(){
    try{
        Pair<T> job = jobs.at(iter);
        iter++;
        return serialization(job);
    }catch(std::out_of_range const& exec){
        std::cout<<"End of Jobs."<<"\n";
        iter=0;
        return "\0";
    }
}

template<class T>
Jobs<T> Jobs<T>::operator=(Jobs<T> j){
    this->range = j.range;
    this->step = j.step;
    this->size_job = j.size_job;
    this->size_jobs = j.size_jobs;
    this->jobs = j.jobs;
    return *this;
}

///SERIALIZATION

template<class T>
char *  Jobs<T>::serialize(Jobs<T> jobs){
    return serialization(jobs);
}

template<class T>
std::string Jobs<T>::serialize(Jobs<T> jobs, bool _str){
    return serialization(jobs);
}

template<class T>
void  Jobs<T>::serialize(char* &str){
    serialization(this, str);
}


template<class T>
void Jobs<T>::deserialize(std::string str){
    *this = deserialization< Jobs<T> >(str);
//    reinitialize(deserialization< Jobs<T> >(str));
}

template<class T>
void  Jobs<T>::deserialize(char * str){
    *this = deserialization< Jobs<T> >(str);
//    reinitialize(deserialization< Jobs<T> >(str));
}

template<class T>
void Jobs<T>::show_array(T* arr, std::size_t size) {
    std::ostringstream ss;
    ss<<"[";
    for(int i=0; i<size; i++){
        ss<<" "<<arr[i]<<",";
    }
    ss<<"\b ]\n";
    printf("The 1d-carray: %s\n", ss.str().c_str());
}

template<class T>
void Jobs<T>::show_array2d(T* arr, std::size_t size) {
    T** M = new T*[size];
    std::size_t begin, end;
    for (int i=0; i<size;i++){
        begin = i*size;
        end = (i+1)*size;
        M[i] = new T[size];
        std::copy(&arr[begin], &arr[end], &M[i][0]);
    }

    std::ostringstream ss;
    ss<<"[";
    for(int i=0; i<size; i++){
        if (i>0) ss<<"\n";
        ss<<"[";
        for(int j=0; j<size; j++)
            ss<<" "<<M[i][j]<<",";
        ss<<"\b ],";
    }
    ss<<"\b]\n";
    printf("--The 2d-carray--\n%s\n", ss.str().c_str());
}
//DETERMING OBJECTS
template class Jobs<long>;
