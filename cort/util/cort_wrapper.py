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
# Software development projects are infamous for missed deadlines and budget overruns.  These are often caused by unexpected issues and obstacles we prefer to think of as anti-patterns.  The software development process is expected to follow a short list of accepted processes patterns but often does not.  Any attempt to reduce these anti-patterns will improve workflow and reduce delays or cost over runs.  This is why many research topics in Software Engineering can be boiled down to this attempt at understanding hindrances to optimal workflow.  We set out to contribute to more than one of these areas.
# To do so, there were many established approaches we could have taken such as surveys, simulation modeling and scientific experiments.  We opted to avoid surveys as perceived processes are often not the real processes that are taking place(W. Van Der Aalst, Weijters, & Maruster, 2004).  Scientific experiments might provide stronger data but they are usually very expensive to carry out (Zelkowitz & Wallace, 1997) (Ur, Yom-tov, & Wernick, 2007) in the software development environment primarily due to the value placed on an engineer’s time. Simulation models are often the popular alternative but many are not sufficiently based on hard data.
# This leaves case studies.  However, despite their popularity in Software Engineering research (Bai, Zhang, & Huang, 2011), case study findings have been criticized as not readily generalizable(Tsang, 2014) at least in part because the “sample size in any case study research project is never going to be large enough to qualify for the use of statistical inference (Easton, 2010).”  However, advocates argue that the most powerful case studies utilize larger datasets and emphasizing those studies “increases the generalizability and validity of the findings (J. L. Jensen & Rodgers, 2001).”  (Lee, 1989) proposes that generalizability can be increased by making confirming observations “when the theory is tested on other empirical circumstances.”  When a topic has very little literature surrounding it, “case research strategy is well-suited to capturing the knowledge of practitioners and developing theories from it” according to (Benbasat, Goldstein, & Mead, 1987)  So quite simply, if we are not in a position to conduct scientific experiments, conduction case studies using a very significant number of entities is a well-supported methodology in software engineering research, despite some criticism in other fields.  In this dissertation, we chose this route.
# So we set out to acquire a comprehensive dataset that would provide the potential to offer insights into numerous sources of software engineering delays and hurdles.  As our attempts to acquire empirical event log data from corporate settings were politely denied and a few times mocked, we sought open source data.  We discovered that the requirements repository of the one of the most significant open source software development (OSSD) organizations, the Apache Software Foundation (Apache), is available to the public in read-only form.  We argue that their ~500,000 tickets and nearly 450 teams  is an usually large sample size for software engineering research and therefore the ideal dataset to acquire in a single effort.  This acquisition effort is detailed in chapter 3.
# We acknowledge that much of our findings will carry much greater weight with the less structured, volunteer dependent and sometimes unconventional open source community instead of the software engineering community as a whole. However, some findings might also apply more broadly. It was established at Microsoft that tickets written by the more experienced team members were met with more confidence (Guo, Zimmermann, Nagappan, & Murphy, 2010).  In other words, experience level influences success in requirements writing.  In chapter 1 we were able to verify this principle also applies in the many Apache teams as well.  In contrast, our findings with regard to volunteerism are likely to be heavily influenced by the unorthodox nature of OSSD.  However, much literature supports the idea that highly motivated developers make more productive employees.  Could the self-driven motivators of OSSD work possibly parallel some of the studies on how best to drive software team members to excel?
# We also argue that if our work primarily applies to OSSD, this is still a significant contribution as OSSD is vital to the industry as a whole for many reasons.  The web may have been cast in the iron shackles designed by MSFT from the start had Apache’s original project (the Apache Web Server) not been made free to the public in 1995.  In recent years, major software organizations deliberately turn over some of their greatest infrastructure projects to Apache so that, not only can the rest of the world utilize these invaluable tools but so that volunteers might help these projects evolve.  Facebook donated Hive and Cassandra, Yahoo donated Hadoop and Adobe donated Flex, just to name a few.  The world of big data is quite dependent on Apache’s clustering framework projects Hadoop and Spark or Apache’s NoSQL stores such as Cassandra or Couchbase.  So any improvement in the processes that these OSSD teams choose will only improve the entire industry’s path forward in countless ways.
# This dissertation is laid out as such.  Chapter one focuses on the beginning of a requirement’s existence as we survey the many contribution levels of Apache participants.  After describing data we have on the contributions from the ~80,000 participants at Apache, we address some research questions regarding how a participant’s experience level influences the types of requirements they tend to submit in addition to the finding on the effectiveness of these requirements mentioned previously.
# Chapter two focuses on how tickets are distributed throughout the team.  We found that the participants that create the tickets tend to have a better track record for finding an owner that is going to complete the work than other participants.  Generally, the tickets that were volunteered for (A.K.A. self-assigned) have been completed at a higher rate than those that were assigned to other participants.  We also discovered a major pattern of delay.  Tickets that are volunteered for but not completed almost directly after being volunteered for take five to ten times as long, depending on the ticket type and other factors, to complete than tickets whose voluntary owner completes the task in that same sitting.  We provide extensive analysis and recommendations regarding this delay causing scenario.
# In chapter three we not only detail how we acquired this data set but also describe a pattern mining platform we built to facilitate repeatable and scalable pattern mining experiments utilizing the pattern mining algorithms provided by the open source tool SPMF.  With this platform, we were able to study each team and their processes individually, provided they had enough tickets to justify the association rules we sought.  Our objective was to establish various measures of effectiveness (especially with regard to completion) and various indicators for process choices for each team.  We were especially interested in how processes of the teams vary in requirements updates, assignment changes (especially abandonment) and exposure to volunteerism.  When comparing these teams by their completion measures found a negative association with requirements changes and an even stronger negative association with the rate of participants removing themselves as ticket owners (abandonment).  Stronger volunteerism indicators are associated with greater completion rates but not nearly as much with the very largest projects to the point that we suggest the effectiveness of occasional delegation may be a factor in the biggest projects succeeding.  We then wrapped up this last investigation of our case study by highlighting some process indicators measures that are common in the teams that score highest on our completion measures.
#
# ''')

# call_cort('''
# Alex Jones, the conspiracist at the helm of the alt-news outlet InfoWars, used an unusual defense in a custody hearing in Texas last week. His ex-wife had accused him of being unstable and dangerous, citing Mr. Jones’s rants on his daily call-in show. (Among his many unconventional stances are that the government staged the Sandy Hook massacre and orchestrated the 9/11 attacks.) Through his attorneys, Mr. Jones countered that his antics are irrelevant to his fitness as a parent, because he is a performance artist whose public behavior is part of his fictional character. In other words, when he tells his audience that Hillary Clinton is running a sex-trafficking operation out of a Washington pizza parlor (an accusation for which he has offered a rare retraction), he is doing so merely for entertainment value.  They will not.  Alex Jones’s audience adores him because of his artifice, not in spite of it. They admire a man who can identify their most primal feelings, validate them, and choreograph their release. To understand this, and to understand the political success of other figures like Donald Trump, it is helpful to know a term from the world of professional wrestling: kayfabe.  Although the etymology of the word is a matter of debate, for at least 50 years “kayfabe” has referred to the unspoken contract between wrestlers and spectators: We’ll present you something clearly fake under the insistence that it’s real, and you will experience genuine emotion. Neither party acknowledges the bargain, or else the magic is ruined.  To a wrestling audience, the fake and the real coexist peacefully. If you ask a fan whether a match or backstage brawl was scripted, the question will seem irrelevant. You may as well ask a roller-coaster enthusiast whether he knows he’s not really on a runaway mine car. The artifice is not only understood but appreciated: The performer cares enough about the viewer’s emotions to want to influence them. Kayfabe isn’t about factual verifiability; it’s about emotional fidelity.
#
# Although their athleticism is impressive, skilled wrestlers captivate because they do what sociologists call “emotional labor” — the professional management of other people’s feelings. Diners expect emotional labor from their servers, Hulkamaniacs demand it from their favorite performer, and a whole lot of voters desire it from their leaders.
#
# The aesthetic of World Wrestling Entertainment seems to be spreading from the ring to the world stage. Ask an average Trump supporter whether he or she thinks the president actually plans to build a giant wall and have Mexico pay for it, and you might get an answer that boils down to, “I don’t think so, but I believe so.” That’s kayfabe. Chants of “Build the Wall” aren’t about erecting a structure; they’re about how cathartic it feels, in the moment, to yell with venom against a common enemy.
#
#
# ''')