//
//  Node.hpp
//  pythonic
//
//  Created by Giorgos Rizos on 7/3/21.
//  Copyright © 2021 Giorgos Rizos. All rights reserved.
//

#ifndef Node_hpp
#define Node_hpp
#include <map>
#include <functional>
#include <string>
#include "Pair.hpp"

template <class T>
class Node{
public:
    typedef std::map<size_t, Node<T> *> NodesMap;
    std::string tag;
    size_t depth; //optional parameter
    
    ///CONSTRUCTORS
    Node();
    Node(std::string tag, T data);
    
    ///GETTERS
    std::size_t get_id();
    T get_data();
    std::size_t get_no_children();
    NodesMap get_children();
    ///OPEARATION
    void new_child(Node<T> *child);
    void delete_child(std::size_t id);
    
    ///OPERATORS
    Node<T> operator=(Node<T> node);
    
private:
    std::size_t id;
    T data;
    NodesMap children;
};
#endif /* Node_hpp */
