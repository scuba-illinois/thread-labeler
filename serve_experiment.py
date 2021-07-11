from flask import Flask, abort, jsonify, request, send_file
from flask_cors import CORS
from random import sample
import json
import sys
import os
import copy
import threading
import signal 
import queue

if len(sys.argv) < 4:
    print(f"Usage: {sys.argv[0]} <experiment-json.in> <all-comments.json.in> <labels-out-dir>")
    exit(1)

experiment_json_filename = sys.argv[1]
all_comments_filename = sys.argv[2]
labels_output_dir = sys.argv[3]
def labels_output_filename(participant_id):
    return os.path.join(labels_output_dir, f'labels_for_participant_{participant_id}.csv')
experiment_json_file = open(experiment_json_filename, 'r')
experiment_json = experiment_json_file.read().strip()
experiment_json_file.close()
experiment = json.loads(experiment_json)

all_comments_file = open(all_comments_filename, 'r')
posts = {}
all_link_ids = set()
for participant in experiment:
    link_ids = list(participant['phase_1']['posts'].keys()) + list(participant['phase_2']['posts'].keys())
    for link_id in link_ids:
        all_link_ids.add(link_id)
for line in all_comments_file.readlines():
    root_comment = json.loads(line)
    current_link_id = root_comment['comment']['link_id']
    if current_link_id in all_link_ids:
        posts[current_link_id] = root_comment
all_comments_file.close()

labels_queue = queue.Queue()
killed = False

def exit_gracefully(signum, frame):
    killed = True
    exit(0)

signal.signal(signal.SIGTERM, exit_gracefully)
signal.signal(signal.SIGINT, exit_gracefully)

def save_labels_worker():
    while not killed:
        labels = labels_queue.get()
        print("Saving labels", labels)
        if not labels or len(labels) == 0:
            continue
        participant_id = labels[0]['participant_id']
        csv_file = open(labels_output_filename(participant_id), 'w')
        header = "id,link_id,participant_id,threaded_interface,phase,removal_time"
        csv_file.write(header + '\n')
        for label in labels:
            row = ",".join([ str(x) for x in label.values() ])
            print("Writing labels", row)
            csv_file.write(row)
            csv_file.write("\n")
            csv_file.flush()
        csv_file.close()

app = Flask(__name__)
CORS(app)

def path_to_target(post, id_to_keep):
    stack = [ post ]
    paths_saved = { post['comment']['id']: '' }
    while len(stack) > 0:
        current = stack.pop()
        for child in current['child_nodes']:
            paths_saved[child['comment']['id']] = current['comment']['id']
            stack.append(child)
    path = [ id_to_keep ]
    current = paths_saved[id_to_keep]
    while current != '':
        path.append(current)
        current = paths_saved[current]
    return path[::-1]

def prune_extraneous(post, comment_ids_in_path):
    children_to_remove = []
    for child in post['child_nodes']:
        if child['comment']['id'] not in comment_ids_in_path:
            children_to_remove.append(child)
    for child in children_to_remove:
        post['child_nodes'].remove(child)
    for child in post['child_nodes']:
        prune_extraneous(child, comment_ids_in_path)

def just_post_ids(post, post_with_ids = { 'id': '', 'child_nodes': [] }):
    post_with_ids['id'] = post['comment']['id']
    for child in post['child_nodes']:
        child_with_id = { 'id': '', 'child_nodes': [] }
        post_with_ids['child_nodes'].append(child_with_id)
        just_post_ids(child, child_with_id)
    return post_with_ids

def print_comment_thread(post_with_ids, indent=0):
    for i in range(indent):
        print(' ' * 3, end='')
    print(post_with_ids['id'])
    for child in post_with_ids['child_nodes']:
        print_comment_thread(child, indent + 1)

def prune_post(post, comments_to_moderate):
    comment_ids_in_path = set()
    for comment_id in comments_to_moderate:
        for path_comment_id in path_to_target(post, comment_id):
            comment_ids_in_path.add(path_comment_id)
    prune_extraneous(post, comment_ids_in_path)

def get_comment(post, comment_id):
    stack = [ post ]
    while len(stack) > 0:
        current = stack.pop()
        if current['comment']['id'] == comment_id:
            return current
        for child in current['child_nodes']:
            stack.append(child)
    assert(False)
    return None

def extract_interesting_comments(current_post, comments_to_moderate):
    non_threaded = { 
                     'comment': current_post['comment'],
                     'child_nodes': [] 
                    }
    for comment_id in comments_to_moderate:
        current = get_comment(current_post, comment_id)
        current['child_nodes'] = []
        non_threaded['child_nodes'].append(current)
    return non_threaded

@app.route('/participant/<int:participant_id>/phase/<int:phase_index>/post/<string:link_id>/', methods=[ 'GET' ])
def threads_from_post(participant_id, phase_index, link_id):
    current_post = copy.deepcopy(posts[link_id])
    comments_to_moderate = experiment[participant_id][f'phase_{phase_index}']['posts'][link_id]
    threaded = experiment[participant_id][f'phase_{phase_index}']['threaded_interface']
    if threaded:
        prune_post(current_post, comments_to_moderate)
    else:
        current_post = extract_interesting_comments(current_post, comments_to_moderate)
    return jsonify(
        { 
            'comments_to_moderate': comments_to_moderate,
            'post': current_post,
            'threaded_interface': threaded,
            'participant_id': participant_id,
            'link_id': link_id
        }
    )

@app.route('/participant/<int:participant_id>/experiment/', methods=[ 'GET' ])
def experiment_for_participant(participant_id):
    if participant_id >= len(experiment):
        abort(404)
        return
    return jsonify(experiment[participant_id])


@app.route('/label/', methods = [ 'POST'] )
def save_labels():
    labels = request.get_json()
    print(labels)
    labels_queue.put(labels)
    return { "saved": True }, 200

@app.route('/participant/<int:participant_id>/labels.csv', methods= [ 'GET' ])
def show_labels(participant_id):
    if os.path.exists(labels_output_filename(participant_id)):
        return send_file(labels_output_filename(participant_id))
    else:
        return abort(500)

if __name__ == '__main__':
    threading.Thread(target=save_labels_worker, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=14000)
    labels_queue.join()