#!/usr/bin/python3
import csv
import json
import sys
import pprint

pp = pprint.PrettyPrinter(indent=4)

class CommentNode:
    def __init__(self, comment):
        self.comment = comment
        self.child_nodes = []
    
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def __str__(self):
        return self.toJSON()

    def __repr__(self):
        return self.toJSON()

def usage():
    print(f"Usage: {sys.argv[0]} <path-to-csv.in> <options>")
    print("Options:")
    print("--help/-h: Show help message")
    print("--confirm/-c: Build discussion thread and count comments to ensure the input/output match")

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        usage()
        exit(0)
    
    if len(sys.argv) < 2:
        usage()
        exit(1)

    csv_filename = sys.argv[1]
    csv_file = open(csv_filename, 'r')
    csv_file_reader = csv.DictReader(csv_file)

    posts = {}
    count = 0
    
    for row in csv_file_reader:
        link_id = row['link_id']
        row_data = \
        {
            'created_utc': row['created_utc'],
            'body': row['body'].replace('\n', ' '),
            'author': row['author'],
            'id': f"t1_{row['id']}",
            'link_id': row['link_id'],
            'parent_id': row['parent_id'],
            'agreement_score': row['agreement_score'],
            'banned_by': row['banned_by'],
        }
        if link_id not in posts:
            posts[link_id] = []
        posts[link_id].append(row_data)
        count += 1

    #for link_id, comments in posts.items():
    #    unique_parents = set([ comment['parent_id'] for comment in comments ])
    #    if len(comments) == 5 and len(unique_parents) > 1:
    #        print(link_id)
    #        print(comments)
    #        return 

    recreate_count = 0 
    confirm = "--confirm" in sys.argv or "-c" in sys.argv
    if confirm:
        for link_id, comments in posts.items():
            root = recreate_thread(link_id, comments)
            recreate_count += confirm_count(root)
        print("Count", count)
        print("Confirm count", recreate_count)
    else:
        for link_id, comments in posts.items():
                print(recreate_thread(link_id, comments).toJSON())


def recreate_thread(link_id, comments):
    parent_comments = {}
    for comment in comments:
        parent_id = comment['parent_id']
        if parent_id not in parent_comments:
            parent_comments[parent_id] = []
        parent_comments[parent_id].append(comment)
    
    root_comment = \
    CommentNode(
        {
            "link_id": link_id,
            "id": link_id,
            "root": True,
            "body": "root",
            "incomplete": False
        }
    )
    build_child_threads(parent_comments, root_comment)
    
    if not root_comment.child_nodes:
        # We don't have enough comments to build a thread, just output flat comments
        root_comment.comment["incomplete"] = True
        for comment in comments:
            root_comment.child_nodes.append(CommentNode(comment))

    return root_comment


def build_child_threads(parent_comments, root):
    root_id = root.comment["id"]
    if root_id in parent_comments:
        root.child_nodes = [ CommentNode(comment) \
                             for comment in parent_comments[root_id] ]
        for child_node in root.child_nodes:
            build_child_threads(parent_comments, child_node)

def confirm_count(root):
    return len(root.child_nodes) + \
            sum([ confirm_count(child_node) for child_node in root.child_nodes ])

if __name__ == '__main__':
    #link_id = 'ab'
    #test = \
    #[
    #        { 'id': '1', 'link_id': link_id, 'parent_id': '2' },                
    #        { 'id': '2', 'link_id': link_id, 'parent_id': '3' },    
    #        { 'id': '3', 'link_id': link_id, 'parent_id': link_id }, 
    #        { 'id': '4', 'link_id': link_id, 'parent_id': '5' },
    #        { 'id': '5', 'link_id': link_id, 'parent_id': link_id }
    #]
    main()