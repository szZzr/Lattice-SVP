//
//  Pair.cpp
//  pythonic
//
//  Created by Giorgos Rizos on 2/2/21.
//  Copyright © 2021 Giorgos Rizos. All rights reserved.
//

#include "Pair.hpp"
///CONSTRUCTORS
template<class T>
Pair<T>::Pair(){
    this->limit = 0;
    this->length = 0;
    this->pos = 0;
}

template<class T>
Pair<T>::Pair(int limit, size_t length, T j){
    this->limit = limit;
    this->length = length;
    this->job = new T[length]();
    this->pos = length-1;
    this->job[pos] = j;
}

template<class T>
Pair<T>::Pair(int limit, size_t length, T* job){
    this->limit = limit;
    this->length = length;
    this->pos = length-1;
    this->job = job;
}

template<class T>
Pair<T>::Pair(int limit, size_t length, T* job, size_t pos){
    /*
     * Basic Constructor
     * limit: Margin of potential values
     * length: Length of task array
     * job: Array with task's data
     * pos: Shows the position of index where worker should process
     */
    this->limit = limit;
    this->length = length;
    this->job = job;
    this->pos = pos;
}

///GETTERS
template<class T>
T* Pair<T>::get_job(){
    return this->job;
}

template<class T>
void Pair<T>::show(){
    std::ostringstream ss;
    ss<<"Limit: "<<limit<<"\nJob: [";
    for(int i=0; i<length; i++){
        ss<<" "<<job[i]<<",";
    }
    ss<<"\b ]\nPosition: "<<pos<<"\n\n";
    std::cout<<ss.str();
}

template<class T>
std::string Pair<T>::display(){
    //Display Pair<T> at inline string
    std::ostringstream ss;
    ss<<"Limit: "<<limit<<" | Job: [";
    for(int i=0; i<length; i++){
        ss<<" "<<job[i]<<",";
    }
    ss<<"\b ] | Position: "<<pos<<"\n";
    return ss.str();
}

template<class T>
Pair<T> Pair<T>::operator=(Pair<T> p){
    limit = p.limit;
    length = p.length;
    pos = p.pos;
    job = new T[length]();
    for(int i=0; i<length;i++){
        job[i] = p.job[i];
    }
    return *this;
}

template<class T>
Pair<T> Pair<T>::tempo(int t){
    Pair<T> task;
    task.length = t;
    task.limit = t;
    task.job = new T[task.length];
    for(int i=0; i<task.length; i++){
        task.job[i] = i+101;
    }
    return task;
}

template<class T>
void Pair<T>::show_(char *a){
    this->show();
    printf("\bAnd this %s", a);
}

template<class T>
void Pair<T>::deserialize(char * str){
    *this = deserialization< Pair<T> >(str);
}


///DETERMING OBJECTS
template class Pair<long>;
template class Pair<int>;
