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


# call_cort('''
# Leslie William Nielsen, OC (11 February 1926 – 28 November 2010) was a Canadian actor, comedian, and producer.[1][2] He appeared in more than 100 films and 150 television programs, portraying more than 220 characters.[3]
#
# Nielsen was born in Regina, Saskatchewan. He enlisted in the Royal Canadian Air Force and later worked as a disc jockey before receiving a scholarship to study theatre at the Neighborhood Playhouse. Making his acting debut in 1950, appearing in 46 live television programs a year. Nielsen made his film debut in 1956, with supporting roles in several drama, western, and romance films produced between the 1950s and the 1970s.
#
# Although his performances in the films Forbidden Planet and The Poseidon Adventure gave him standing as a serious actor, Nielsen later gained enduring recognition for his deadpan comedy roles during the 1980s, after being cast against type for the Zucker, Abrahams and Zucker comedy film Airplane!. In his routines, Nielsen specialized in his portrayal of characters oblivious to and complicit in their absurd surroundings, which gave him a reputation as a comedian.[4] Airplane! marked Nielsen's turning point, which made him "the Olivier of spoofs" according to film critic Roger Ebert;[5] his work on the film also led to further success in the genre with The Naked Gun film series, which are based on their earlier short-lived television series Police Squad!, in which he also starred. Nielsen received a variety of awards and was inducted into the Canada and Hollywood Walks of Fame.
# ''')
#
# call_cort('''
# Washingtonn (CNN)After puzzling comments about 19th Century abolitionist Frederick Douglass and marveling that no one knew Abraham Lincoln was a Republican, President Donald Trump has just unloaded another historical non sequitur.
#
# In the latest strange aside, Trump said that Andrew Jackson, the populist rabble-rousing President with whom he has begun to claim political kinship, had strong thoughts about the Civil War -- even though he died 16 years before the conflict broke out.
# "He was really angry that -- he saw what was happening with regard to the Civil War," Trump said in an interview with Salena Zito, a Washington Examiner reporter and CNN contributor, on Sirius XM radio. "He said, 'There's no reason for this.' "
# Trump's comment makes little sense because Jackson died in 1845 and therefore could have had limited knowledge about events leading up to the conflagration pitting his native South against Northern states.
# It was not clear whether Trump might have been trying to suggest that Jackson had extreme foresight and believed that a clash between the North and the South was inevitable sooner or later over the issue of slavery.
# Donald Trump just gave two incredibly bizarre (and fact-free) interviews
# Donald Trump just gave two incredibly bizarre (and fact-free) interviews
# But considering the fact that Jackson was a slave owner himself, it seems unlikely that he held any views that would not have focused on preserving an institution that has come to be viewed as a stain in US history.
# The facts
# The comments focused fresh attention on the President's sometimes sketchy relationship with the facts of history -- and underlined yet again just how different he is from many of his predecessors in the Oval Office.
# Most Presidents spend a lifetime studying their political heroes and take solace in accounts of their administrations and trials when they are under pressure. Rarely a week went by without President Barack Obama referencing Lincoln, and George W. Bush was a voracious reader who powered through presidential biographies in a marathon reading contest with Karl Rove.
# But Trump gives no sense that he is widely read or has deeply researched the men who had his job before him -- a fact that chills critics who argue he has little understanding of the crucial position to which he was elected. Trump's recent comments about how hard it is to enact laws in Congress and apparent unfamiliarity with details of his own health care reform plan have also raised doubts about the depth of his understanding of Washington and the presidency.
# When he's talking about history, Trump often leaves the impression that he is discovering facts and events for the first time, marveling at them like a newcomer.
# That may be one reason why his historical analogies often come across as off key or at odds with the facts.
#
# Essay: Dishonesty shapes Trump's presidency 00:58
# Does it matter?
# But Trump's historical missteps also raise another question. Does it matter that the President of the United States seems to lack knowledge and understanding of the key events of his nation's past and the principles that underpin them?
# On the one hand, it's doesn't seem too much of a stretch to believe that the US President should know, or might benefit from, the insights and stories of the presidencies that unfolded before he became commander-in-chief.
# But on the other, no one voted for Trump because they thought he was professorial -- in fact his spontaneous, simplistic way of speaking may have come as a relief to some voters who grew tired of Obama's discursive, intellectual style.
# In what became a cliche of the 2016 election, Trump's voters often said that the reason they flocked to the reality star and real estate magnate is that he was prepared to say things, free of the constraints of political correctness, that they had long yearned for a presidential candidate to say.
# Those voters seem unlikely to reject Trump just because of a few strange remarks about Andrew Jackson and probably care little that he eschews the intellectualism of many of his predecessors. In fact, anti-intellectualism and excoriating political elites in the US was at the center of his upstart political project.
# And while he might not be book smart when it comes to history, Trump did manage to build a business empire and personality cult around himself that offered him notoriety and a life in the public eye that he seemed to crave.
# He had the political intelligence as well -- more than any professional politician in last year's election -- to understand and give voice to the frustrations and complaints of a group of heartland voters who felt disenfranchised and ignored by a modern economy built by Washington elites.
# He's also not the only President to face questions about his intellectual heft or basic knowledge. Ronald Reagan was often mocked as dumb and unseasoned, yet had one of the most successful presidencies of the 20th century.
# Supreme Court Justice Oliver Wendell Holmes Jr. is said by most historians to have been referring to Franklin Roosevelt when he diagnosed the Democratic president as having a second-class intellect but a first-class temperament.
#
# Trump: Why was there a Civil War? 01:59
# 'Why was there a Civil War?'
# But Trump's interpretation of history, which is often rudimentary and not anchored in fact, takes the debate about presidential knowledge and understanding to a new level.
# Critics say that it is a sign of a worrying lack of intellectual curiosity, preparation and an unwillingness to submit to accepted truths that contradict his own version of reality.
# Trump's interview with Zito was also revealing because it went on to cover the idea of leadership, and the President appeared to be drawing a parallel between him and Jackson.
# "Why was there the Civil War? Why could that one not have been worked out?" Trump told Zito.
# "I mean, had Andrew Jackson been a little bit later, you wouldn't have had the Civil War. He was a very tough person, but he had a big heart."
# The fact that Trump admires Jackson because he was tough and had a big heart appears to equate with Trump's view of himself and the idea that a President of sufficient personality and muscle could have averted the epochal events -- like the Civil War. Jackson was a revered general, was outspoken and aggressive and was the first President elected from west of the Alleghenies, giving him a heartland heritage with which Trump, who has repeatedly shown his admiration of great military men, may identify.
# The President visited Jackson's home in Tennessee, the Hermitage, in March to lay a wreath on the former President's 250th birthday and also drew links between their visions on trade.
# "He imposed tariffs on foreign countries to protect American workers. That sounds very familiar. Wait 'til you see what's going to be happening pretty soon, folks," Trump joked.
# Trump also brought a portrait of Jackson into the Oval Office after he was inaugurated, and It's not surprising he should identify with someone who is a hero of his political guru, Steve Bannon.
# Bannon told The Washington Post in January, that Trump's inaugural address put him in mind of the 7th President.
# "I don't think we've had a speech like that since Andrew Jackson came to the White House," Bannon told the paper. "But you could see it was very Jacksonian. It's got a deep, deep root of patriotism there."
# A 12-inch talking Trump doll is on display at a toy store in New York in September 2004.
# Photos: Donald Trump's rise
# A 12-inch talking Trump doll is on display at a toy store in New York in September 2004.
# Toughness as virtue
# Trump has made clear during his first 102 days in office that he sees toughness as a virtue, but he has also argued -- in the case of his strikes against Syria for its use of chemical weapons for instance -- that he has humanitarian impulses.
# Trump has also courted tough, strong leaders around the world, like Filipino President Rodrigo Duterte, Turkish President Recep Tayyip Erdogan and Egyptian President Abdel Fattah el-Sisi even if their behavior and treatment of their people and democracy offends those who believe that promoting human rights should be put at the center of US foreign policy.
# Trump's Jacksonian stumble is not the first time that he has brought ridicule upon himself by mangling the facts of history. Earlier this year, the President seemed to imply that Douglass, who died in 1895, was still alive.
# "Frederick Douglass is an example of somebody who's done an amazing job and is being recognized more and more, I notice," Trump said at the White House in February at an event recognizing African American history month.
# Trump also seemed impressed that Lincoln, who is often judged by historians as the greatest president, was a Republican -- even though it is one of the most familiar historical facts that he was the first Republican Party president.
# "Great president. Most people don't even know he was a Republican," Trump said back in in March. "Does anyone know? Lot of people don't know that."
# "We have to build that up a little bit more let's take an ad, let's use one of the those PACs," he said.
# As always with Trump, it was difficult to know whether the President was being genuine or was talking with his tongue in his cheek.
# But given the President's off-the-cuff speaking style and willingness to hold forth on subjects in which he seems to lack a deep grounding, it's unlikely he has committed his last historical gaffe.
# ''')


# call_cort('''
# Bipartisan congressional negotiators reached a critical agreement late Sunday on a massive spending bill that if approved by the House and Senate would fund the government through the end of September, senior aides from both parties told CNN.
#
# The plan would add billions for the Pentagon and border security but would not provide any money for President Donald Trump's promised border wall with Mexico,
# Votes in both chambers are expected by the end of the week.
#
# The deal was reached after weeks of tense but steady negotiations between Republicans and Democrats on Capitol Hill and the White House, who battled over spending priorities but who were equally determined to avoid a politically fraught government shutdown. Republicans, who control Congress and the White House, were particularly wary of a shutdown on their watch.
# What's in and what's out in the latest government spending bill
# Senate Minority Leader Chuck Schumer released a statement Sunday evening saying the agreement is consistent with his party's principles.
# "This agreement is a good agreement for the American people, and takes the threat of a government shutdown off the table," the New York Democrat said in a statement.
# House Democratic Leader Nancy Pelosi also praised the proposal, saying in a statement "we have made significant progress improving the omnibus bill."
#
# Trump's presidency, the latest on Capitol Hill and political news across the country — get the most important political news delivered to your inbox. By subscribing, you agree to our privacy policy.
#
# Enter email address
# SUBSCRIBE
# "Now, the Members of our Caucus will assess the whole package and weigh its equities," the California Democrat said in the statement.
# Aides in each party disputed some characterizations from the other side as to what made into the final proposal but one of the key aspects they agreed on: The bill has $1.5 billion for border security, including for technology and fixing existing infrastructure but it doesn't allow the money to spent on building Trump's wall. There is no money provided for a deportation force and there are no cuts of federal monies to so-called sanctuary cities.
# RELATED: Donald Trump just caved on the border wall (or did he?)
# Trump's demand for the border wall down payment was rejected by Democrats. They decried the controversial project -- and key Trump campaign promise -- as immoral and premature since Trump has not detailed plans for building the multibillion dollar wall he had vowed Mexico would pay for anyway.
# Aides also agreed that the bill includes billions in new defense spending, including for the global war on terrorism, a major demand from Republicans.
# Chances the Trump tax proposal gets through Congress? &#39;Slim-to-none&#39;
# Chances the Trump tax proposal gets through Congress? 'Slim-to-none'
# In the proposal, there are no cuts to funding for Planned Parenthood, a demand from Democrats.
# Funding for the National Institute of Health is increased by $2 billion and there is additional money for clean energy and science funding.
# Negotiators also agreed to make a permanent fix for miners health insurance and to provide $295 million for Puerto Rico Medicaid. There is also disaster aid package that includes funding for California, West Virginia, Louisiana, North Carolina. There is increased funding for transit infrastructure grants and to fight the opioid epidemic, and year-round Pell Grants were restored.
#
# Talks had also stalled over a threat by Trump to cut off Obamacare subsidies paid to insurance companies to reduce the out-of-pocket expenses of some lower-income users of the Affordable Care Act, but Trump backed off that demand in the face of harsh criticism from Democrats.
# The subsidies will stay in place as Republicans continue their long-stalled effort to repeal Obamacare, something Trump and his aides hope to revive as early as this week.
# The deal means a government shutdown next Friday, when agencies are set to run out of money, is unlikely. Last Friday, Congress passed a one-week stopgap spending bill when it became clear negotiators needed a bit more time to finalize an agreement.
# This story has been updated and will be updated to include new developments.
#
# ''')