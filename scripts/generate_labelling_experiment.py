#!/usr/bin/python3
'''
generate_labelling_experiment.py:
* Generates a JSON object containing randomly sampled false positive and false negative comments from the Crossmod reporting epxeriment dataset
* Used for generating the data for running the Crossmod labelling experiment
* More information about the Crossmod labelling experiment can be found here: https://www.notion.so/adishy/Crossmod-Labelling-Experiment-393b4498578345609c29c32f29d9427f
Author: Aditya Manjusha Shylesh (adishy@umich.edu)
'''

import json
import random
import sys

def print_usage():
    print(f'Usage: {sys.argv[0]} <reporting-experiment-json> <participant-count> <each-participant-moderates-n-comments>')
    print('Argument 0: File path for reporting experiment JSON')
    print('Argument 1: An integer specifying participant count (optional argument)')
    print('Argument 2: An integer specifying comment count each participant gets (optional argument)')

def add_to_phase(start, end, posts, comments):
    for i in range(start, end):
        current_link_id = comments[i]['link_id']
        current_id = comments[i]["id"]
        if current_link_id in posts:
            posts[current_link_id].append(current_id)
        else:
            posts[current_link_id] = [ current_id ]

def add_all_interesting(thread, false_positives, false_negatives):
    if 'root' not in thread['comment']:
        if 'agreement_score' not in thread['comment']:
            print(thread['comment'])
        assert('agreement_score' in thread['comment'])
        crossmod_removed = float(thread['comment']['agreement_score']) >= 0.85
        banned_by_mods = len(thread['comment']['banned_by']) > 0
        # Row marked as "to be removed" by Crossmod but not removed by moderators
        if crossmod_removed and not banned_by_mods:
            false_positives.append( 
                                    {
                                      'id': thread['comment']['id'],
                                      'link_id': thread['comment']['link_id'] 
                                    }
                                   )
        # Row removed by moderators but Crossmod did NOT markeas "to be removed" 
        if not crossmod_removed and banned_by_mods:
            false_negatives.append( 
                                    {
                                      'id': thread['comment']['id'],
                                      'link_id': thread['comment']['link_id'] 
                                    }
                                   )
    for child in thread['child_nodes']:
        add_all_interesting(child, false_positives, false_negatives)

def sample_interesting_comments(json_filename, participant_count, each_participant_sees):
    '''
        Takes the reporting experiment JSON dataset and generates a JSON object with randomly sampled
        false positive and false negative comments to run a Crossmod labelling experiment.
    '''
    # For reading reporting experiment CSV file
    json_file = open(json_filename, 'r')

    all_false_positives = []
    all_false_negatives = []
    for thread in json_file.readlines():
        current_thread = json.loads(thread)
        add_all_interesting(current_thread, all_false_positives, all_false_negatives)
    # We show the same set of randomly sampled comments with different interfaces to every pair of participants
    false_positives = random.sample(all_false_positives, each_participant_sees * int(participant_count / 2))
    false_negatives = random.sample(all_false_negatives, each_participant_sees * int(participant_count / 2))

    experiment = []
    fp_threaded = False
    fn_threaded = True
    current_start = 0
    for i in range(participant_count):
        participant_experiment = \
        {
            # Participants are shown false positive comments
            'phase_1': {
                'posts': {},
                'threaded_interface': fp_threaded,
                'comments_count': 0
            },

            # Participants are show false negative comments
            'phase_2': {
                'posts': {},
                'threaded_interface': fn_threaded, 
                'comments_count': 0
            },
            'participant_id': i
        }

        fp_posts = participant_experiment['phase_1']['posts']
        fn_posts = participant_experiment['phase_2']['posts']

        # Store sampled false positive comments by link_id
        add_to_phase(current_start,
                     current_start + each_participant_sees,
                     fp_posts,
                     false_positives)
        # Check comment count
        for key, value in fp_posts.items():
            participant_experiment['phase_1']['comments_count'] += len(value)
        assert(participant_experiment['phase_1']['comments_count'] == each_participant_sees) 
        # Store sampled false negative comments by link_id
        add_to_phase(current_start,
                     current_start + each_participant_sees,
                     fn_posts,
                     false_negatives)
        # Check comment count
        for key, value in fn_posts.items():
             participant_experiment['phase_2']['comments_count'] += len(value)
        assert(participant_experiment['phase_2']['comments_count'] == each_participant_sees)

        experiment.append(participant_experiment) 

        # Change interface type for next participant
        fp_threaded = (not fp_threaded)
        fn_threaded = (not fn_threaded)
        # Set to next comment range for following pair of participants
        if i % 2 == 1:
            current_start = i * each_participant_sees
    
    experiment_json = json.dumps(experiment,
                                 indent=4,
                                 sort_keys=True)
    print(experiment_json)

def main():
    if len(sys.argv) < 2: 
        print_usage()
        exit(1)
    if sys.argv[1] == '--help':
        print_usage()
        exit(0) 
    reporting_experiment_csv_filename = sys.argv[1]
    participant_count = 4
    if len(sys.argv) > 2:
        participant_count = int(sys.argv[2])
    # Making participant count an even number (shouldn't affect the experiment if there are an odd number of participants)
    if participant_count % 2 == 1:
        participant_count += 1
    each_participant_sees = 200
    if len(sys.argv) > 3:
        each_participant_sees = int(sys.argv[3])
    sample_interesting_comments(reporting_experiment_csv_filename,
                                participant_count,
                                each_participant_sees)

if __name__ == '__main__':
    main()
