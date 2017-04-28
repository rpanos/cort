# -*- coding: utf-8 -*-
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
from cort.coreference.approaches.mention_ranking import RankingPerceptron
from cort.coreference.clusterer import all_ante

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

    # perceptron = import_helper.import_from_path(perceptron_path)(
    #     priors=priors,
    #     weights=weights,
    #     cost_scaling=0
    # )

    perceptron = RankingPerceptron(
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
        # import_helper.import_from_path(clusterer_path)
        all_ante
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

# call_cort("""There are places I'll remember
#             All my life, though some have changed
#             Some forever, not for better
#             Some have gone and some remain
#             All these places have their moments
#             With lovers and friends I still can recall
#             Some are dead and some are living
#             In my life, I've loved them all
#
#             But of all these friends and lovers
#             There is no one compares with you
#             And these memories lose their meaning
#             When I think of love as something new
#             Though I know I'll never lose affection
#             For people and things that went before
#             I know I'll often stop and think about them
#             In my life, I love you more
#
#             Though I know I'll never lose affection
#             For people and things that went before
#             I know I'll often stop and think about them
#             In my life, I love you more
#             In my life-- I love you more """)


# call_cort('''
# Alex Jones, the conspiracist at the helm of the alt-news outlet InfoWars, used an unusual defense in a custody hearing in Texas last week. His ex-wife had accused him of being unstable and dangerous, citing Mr. Jones’s rants on his daily call-in show. (Among his many unconventional stances are that the government staged the Sandy Hook massacre and orchestrated the 9/11 attacks.) Through his attorneys, Mr. Jones countered that his antics are irrelevant to his fitness as a parent, because he is a performance artist whose public behavior is part of his fictional character. In other words, when he tells his audience that Hillary Clinton is running a sex-trafficking operation out of a Washington pizza parlor (an accusation for which he has offered a rare retraction), he is doing so merely for entertainment value.  They will not.  Alex Jones’s audience adores him because of his artifice, not in spite of it. They admire a man who can identify their most primal feelings, validate them, and choreograph their release. To understand this, and to understand the political success of other figures like Donald Trump, it is helpful to know a term from the world of professional wrestling: kayfabe.  Although the etymology of the word is a matter of debate, for at least 50 years “kayfabe” has referred to the unspoken contract between wrestlers and spectators: We’ll present you something clearly fake under the insistence that it’s real, and you will experience genuine emotion. Neither party acknowledges the bargain, or else the magic is ruined.  To a wrestling audience, the fake and the real coexist peacefully. If you ask a fan whether a match or backstage brawl was scripted, the question will seem irrelevant. You may as well ask a roller-coaster enthusiast whether he knows he’s not really on a runaway mine car. The artifice is not only understood but appreciated: The performer cares enough about the viewer’s emotions to want to influence them. Kayfabe isn’t about factual verifiability; it’s about emotional fidelity.
#
# Although their athleticism is impressive, skilled wrestlers captivate because they do what sociologists call “emotional labor” — the professional management of other people’s feelings. Diners expect emotional labor from their servers, Hulkamaniacs demand it from their favorite performer, and a whole lot of voters desire it from their leaders.
#
# The aesthetic of World Wrestling Entertainment seems to be spreading from the ring to the world stage. Ask an average Trump supporter whether he or she thinks the president actually plans to build a giant wall and have Mexico pay for it, and you might get an answer that boils down to, “I don’t think so, but I believe so.” That’s kayfabe. Chants of “Build the Wall” aren’t about erecting a structure; they’re about how cathartic it feels, in the moment, to yell with venom against a common enemy.
#
#
# ''')