//
//  Node.cpp
//  pythonic
//
//  Created by Giorgos Rizos on 7/3/21.
//  Copyright © 2021 Giorgos Rizos. All rights reserved.
//

#include "Node.hpp"
///CONSTRUCTORS

template<class T>
Node<T>::Node(){
//    this->data = NULL;
}

template<class T>
Node<T>::Node(std::string tag, T data){
    this->tag.assign(tag);
    this->data = data;
    std::hash<std::string> hash_tag;
    this->id = hash_tag(tag);
}

///GETTERS
template<class T>
std::size_t Node<T>::get_id(){
    return id;
}

template<class T>
T Node<T>::get_data(){
    return data;
}

template<class T>
std::size_t Node<T>::get_no_children(){
    return children.size();
}


template<class T>
std::map<size_t, Node<T> *> Node<T>::get_children(){
    return children;
}


///OPERATION
template<class T>
void Node<T>::new_child(Node<T> *child){
    children.insert( {child->get_id(), child} );
}

template<class T>
void Node<T>::delete_child(std::size_t id){
    children.erase(id);
}


///OPERATORS
template<class T>
Node<T> Node<T>::operator=(Node<T> node){
    this->tag.assign(node.tag);
    this->id = node.get_id();
    this->children = node.get_children();
    this->data = node.data;
    return *this;
}

///DETERMING OBJECTS
template class Node<int>;
template class Node<long>;
template class Node<Pair<long> >;
template class Node<Pair<int> >;
