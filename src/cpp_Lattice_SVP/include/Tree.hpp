//
//  Tree.hpp
//  pythonic
//
//  Created by Giorgos Rizos on 7/3/21.
//  Copyright © 2021 Giorgos Rizos. All rights reserved.
//

#ifndef Tree_hpp
#define Tree_hpp
#include <stack>
#include <queue>
#include <unordered_set>
#include "Node.hpp"

template <class T>
class Tree{
public:
    enum Tree_Mode {DFS, BFS};
    typedef std::map<size_t, Node<T> *> NodesMap;
    typedef std::unordered_set<std::size_t> LeavesSet;
    Node<T> *root;
    ///CONSTRUCTORS
    Tree();
    Tree(Node<T> *root);

    ///GETTERS
    NodesMap get_vertices();
    std::size_t get_height();
    std::size_t get_no_nodes();
    LeavesSet get_leaves();
    Node<T>* find_node(std::size_t node_id);

    ///OPEARATION
    void insert_node(Node<T> *root); //Root Node
    void insert_node(size_t parent_id, Node<T> *node);
    Node<T>* create_node(std::string tag , T data); //Root Node
    Node<T>* create_node(size_t parent_id, std::string tag , T data);
    std::queue<size_t> dfs(Node<T> *node);
    std::queue<size_t> bfs(Node<T> *node);
    void show(Tree::Tree_Mode mode=BFS);
    
    ///OPERATOR
    Tree<T> operator=(Tree<T> tree);
    
    ///ITERATOR
    struct Iterator{
        ///TAGS
        using iterator_category = std::forward_iterator_tag;
        using difference_type = std::ptrdiff_t;
        using value_type = Node<T>;
        using pointer = Node<T>*;
        using reference = Node<T>&;
        
        std::queue<Node<T>*> bfs_q;
        
        ///CONSTRUCTORS
        Iterator() {}
        Iterator(pointer ptr): _ptr(ptr) {}

        reference operator*(){ return *_ptr;}
        pointer operator->() {return _ptr;}
        
        Iterator& operator++();//prefix
        Iterator operator++(int);//postfix
        
        friend bool operator== (const Iterator& a, const Iterator& b) { return a._ptr == b._ptr; };
        friend bool operator!= (const Iterator& a, const Iterator& b) { return a._ptr != b._ptr; };
    private:
        pointer _ptr;
    };
    
    Iterator begin();
    bool end(Iterator it);
private:
    NodesMap vertices;
    LeavesSet leaves;
    std::size_t height;

    inline void new_vertex(std::size_t parent_id, Node<T> *node);
};

#endif /* Tree_hpp */
