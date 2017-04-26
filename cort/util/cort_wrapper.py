
# from __future__ import print_function  ###???
import argparse
import codecs
import logging
import pickle
import sys


from cort.preprocessing import pipeline
from cort.core import mention_extractor
from cort.coreference import cost_functions
from cort.coreference import experiments
from cort.coreference import features
from cort.coreference import instance_extractors
from cort.util import import_helper
from cort.coreference.approaches.mention_ranking import extract_substructures

def call_cort(text_blob):


    mention_features = [
        features.fine_type,
        features.gender,
        features.number,
        features.sem_class,
        features.deprel,
        features.head_ner,
        features.length,
        features.head,
        features.first,
        features.last,
        features.preceding_token,
        features.next_token,
        features.governor,
        features.ancestry
    ]

    pairwise_features = [
        features.exact_match,
        features.head_match,
        features.same_speaker,
        features.alias,
        features.sentence_distance,
        features.embedding,
        features.modifier,
        features.tokens_contained,
        features.head_contained,
        features.token_distance
    ]

    # todo make sure these are exact!
    model_abs = '/Users/ryanpanos/Documents/code/cort_experiments/models/model-pair-train+dev.obj'  #OMG evil!
    # perceptron_path = 'cort.coreference.approaches.mention_ranking.RankingPerceptron'
    # extractor_path = ' cort.coreference.approaches.mention_ranking.extract_substructures'
    perceptron_path = 'cort.coreference.approaches.mention_ranking.RankingPerceptron'
    extractor_path = ' coreference.approaches.mention_ranking.extract_substructures'
    corenlp_path = '/Users/ryanpanos/Documents/code/StanfordNLP/stanford-corenlp-full-2016-10-31/'  #OMG evil!
    clusterer_path = 'cort.coreference.clusterer.all_ante'

    # logging.info("Loading model.")
    print("Loading model . ... (this takes a while) ")
    priors, weights = pickle.load(open(model_abs, "rb"))
    print("Model loaded.")

    perceptron = import_helper.import_from_path(perceptron_path)(
        priors=priors,
        weights=weights,
        cost_scaling=0
    )

    extractor = instance_extractors.InstanceExtractor(
        # import_helper.import_from_path(extractor_path),
        extract_substructures,
        mention_features,
        pairwise_features,
        cost_functions.null_cost,
        perceptron.get_labels()
    )

    logging.info("Reading in and preprocessing data.")
    p = pipeline.Pipeline(corenlp_path)

    testing_corpus = p.run_on_blob("corpus", text_blob)

    logging.info("Extracting system mentions.")
    for doc in testing_corpus:
        doc.system_mentions = mention_extractor.extract_system_mentions(doc)

    mention_entity_mapping, antecedent_mapping = experiments.predict(
        testing_corpus,
        extractor,
        perceptron,
        import_helper.import_from_path(clusterer_path)
    )

    testing_corpus.read_coref_decisions(mention_entity_mapping, antecedent_mapping)

    logging.info("Write output to file.")

    output_ls = []
    for doc in testing_corpus:
        output = doc.to_simple_output()
        # my_file = codecs.open(doc.identifier + "." + args.suffix, "w", "utf-8")
        # my_file.write(output)
        print " output: \n" + output
        # my_file.close()
        output_ls.append(output)

    logging.info("Done.")



    return

call_cort("""There are places I'll remember
            All my life, though some have changed
            Some forever, not for better
            Some have gone and some remain
            All these places have their moments
            With lovers and friends I still can recall
            Some are dead and some are living
            In my life, I've loved them all

            But of all these friends and lovers
            There is no one compares with you
            And these memories lose their meaning
            When I think of love as something new
            Though I know I'll never lose affection
            For people and things that went before
            I know I'll often stop and think about them
            In my life, I love you more

            Though I know I'll never lose affection
            For people and things that went before
            I know I'll often stop and think about them
            In my life, I love you more
            In my life-- I love you more """)