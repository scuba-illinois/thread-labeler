#!/usr/bin/python3
import json
import sys

class MaxList:
    def __init__(self, max_elements = 100):
        self.values = set()
        self.max_elements = max_elements

    def push(element, weight):
        self.values.push((element, weight))
        if len(self.values) > self.max_elements:
            min_weight = 10_000_000
            to_erase = None
            for i in self.values:
                if i[1] < min_weight:
                    to_erase = i
            self.values.remove(to_erase)

    def __repr__(element):
        return str(element.values)

def save_top_comments(posts, saved, weight):
    for post in posts:
        saved.push(post["link_id"], weight(post))

def get_false_postives(root_comment):
    count = 0
    for comment in root_comment.child_nodes:
        if float(comment["agreement_score"]) >= 0.85 and len(comment["banned_by"]) == 0:
            count += 1
        count += get_false_postives(comment)
    return count

def get_false_negatives(root_comment):
    count = 0
    for comment in root_comment.child_nodes:
        if float(comment["agreement_score"]) < 0.85 and len(comment["banned_by"]) > 0:
            count += 1
        count += get_false_negatives(comment)
    return count

def main():
    #posts = {}
    #false_positives = MaxList(500)
    #false_negatives = MaxList(500)
    #if len(sys.argv) < 2:
    #    print(f"Usage: {sys.argv[0]} <json-file.in>")
    #    exit(1)
    #input_json_filename = sys.argv[1]
    #input_json_file = open(input_json_filename, 'r')
    #for line in input_json_file.readlines():
    #    root_comment = json.loads(line)
    #    if root_comment["incomplete"]:
    #        continue
    #    posts[root_comment["link_id"]] = root_comment
    #save_top_comments(posts, false_positives, get_false_postives)
    #save_top_comments(posts, false_negatives, get_false_negatives)
    #print("False Positives", false_positives)
    #print("False Negatives", false_negatives)


