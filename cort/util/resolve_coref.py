
from cort_wrapper import call_cort
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
# http://stackoverflow.com/questions/10408927/how-to-get-all-sub-elements-of-an-element-tree-with-python-elementtree

# def resolve_coref(text_blog):
#
#     xml_resolutions = call_cort(text_blog)
#
#     root = ET.fromstring(xml_resolutions)

# todo: move this to a settings constant type file

STD_PROFORMS = ["it", "they", "him", "her", "he", "she", "there", "our", "we"]

def strip_extra_white_space(full_string):

    return re.sub('\s\s+', ' ', full_string)

def add_to_dicts(mention_node, mention_id_to_text_dict, mention_ent_id_to_ant_id_dict):
    print " text :" + str(mention_node.text)
    # print " text " + str(mention_node.dump('text'))
    # dump
    if (mention_node.get('id')):

        mention_id_to_text_dict[int(mention_node.get('id'))] = strip_extra_white_space(mention_node.text)
        if int(mention_node.get('id')) == 0:
            print " --------------------------- ZERO: " + mention_node.text
            print " AFTER: " + str(mention_id_to_text_dict[int(mention_node.get('id'))])

        if (mention_node.get('antecedent')):
            mention_ent_id_to_ant_id_dict[int(mention_node.get('id'))] = mention_node.get('antecedent')  # pointless?

    return mention_id_to_text_dict, mention_ent_id_to_ant_id_dict


def get_branch_data(root, mention_id_to_text_dict, mention_ent_id_to_ant_id_dict, is_sub=False):
    if is_sub:
        search_node_str = './/mention/mention'
    else:
        search_node_str = 'mention'


    if len(root.findall(search_node_str)) == 0:
        print str(is_sub) + "-------------> how is this zero? " + ET.tostring(root)
    else:
        print str(is_sub) + "---> do have thismany nodes: " + str(len(root.findall(search_node_str))) # + " | " + ET.tostring(root)


    for mention_node in root.findall(search_node_str):


        # if (mention_node.get('entity')):
        #     print " ENTITY "
        mention_id_to_text_dict, mention_ent_id_to_ant_id_dict = add_to_dicts(mention_node,
                                                                                    mention_id_to_text_dict,
                                                                                  mention_ent_id_to_ant_id_dict)

        if len(mention_node.findall('mention')) > 0:

            # todo maybe reparse?  but from string? ET.parse(file_name)
            mention_node_redone = ET.fromstring("<hack entity='ym'>" + ET.tostring(mention_node) + "</hack>")
            print "DOING NEXT BRANCH " + ET.tostring(mention_node_redone)
            mention_id_to_text_dict, mention_ent_id_to_ant_id_dict = get_branch_data(mention_node_redone, mention_id_to_text_dict,
                                                                                         mention_ent_id_to_ant_id_dict,
                                                                                         is_sub=True)
            print "*** Done with branch "
        else:
            print " ** no more subs :" + str(mention_node.text)
        # else:
        #     print " no entity? mention_node: " + ET.tostring(mention_node)

    return mention_id_to_text_dict, mention_ent_id_to_ant_id_dict


## CONVERT text and Add TAIL!!!
def convert_text_this_node(this_node, mention_id_to_text_dict, mention_ent_id_to_ant_id_dict):
    node_text = ''
    if this_node.get('id'):

        if this_node.get('antecedent'):
            print ">> PROFORM:  "  + this_node.text
            print ">> LOOKING FOR antecedant " + this_node.get('antecedent')
            # print ">> FOUND: " + mention_id_to_text_dict[mention_ent_id_to_ant_id_dict[this_node.get('antecedent')]]
            print ">> FOUND: " + mention_id_to_text_dict[int(this_node.get('antecedent'))]

            node_text += strip_extra_white_space(this_node.text) + ' ' + mention_id_to_text_dict[int(this_node.get('antecedent'))] #todo add a seperator?
    else:
        print " NO id?? " + ET.tostring(this_node)

    # node_text += this_node.tail  #761
    return node_text


def give_substitute_term(id_num, entity_dict_of_lists):
    longest_text = ''
    if int(id_num) not in entity_dict_of_lists:
        print " %% no " + str(id_num) + " entity_dict_of_lists >> "
        return None

    entity_lists = entity_dict_of_lists[int(id_num)]
    for ent_node in entity_lists:
        if 'entity' in ent_node and 'antecedent' not in ent_node:

            if strip_extra_white_space(ent_node['text']) in STD_PROFORMS:
                print " >> *Top* text is proform?? " + strip_extra_white_space(ent_node['text'])
                ## TODO consider another?

            return ent_node['text']
        if len(longest_text) < strip_extra_white_space(ent_node['text']):
            longest_text = strip_extra_white_space(ent_node['text'])

    print " DIDNT find entyity without ANTECEDANT  "
    return longest_text


            # entity_dict_of_lists(mention_node.get('entity'))
            #
            # if mention_node.get('antecedent'):


# TODO: use OOD to encapsulate and stop passing the dicts
## MAYBE return node just done then does remove(subelement)
# CURRENTLY this is "get all data from all nodes" but not the content itself of this node TODO: rethink
# def accumulate_branch_text(root, mention_id_to_text_dict, mention_ent_id_to_ant_id_dict, is_sub=False):
#     if is_sub:
#         search_node_str = './/mention/mention'  ## THIS IS SO HACKY TODO: refrain from embracing evil
#     else:
#         search_node_str = 'mention'
#
#     # treat each node the same and return that inner awesome translated
#     accumulated_txt = ''
#
#     for mention_node in root.findall(search_node_str):
#         # Convert this node
#         accumulated_txt += convert_text_this_node(mention_node, mention_id_to_text_dict, mention_ent_id_to_ant_id_dict )
#         # Does it have children?
#         if len(mention_node.findall('mention')) > 0:
#
#             # INNER MENTION!!
#             # todo maybe reparse?  but from string? ET.parse(file_name)
#             mention_node_redone = ET.fromstring("<hack entity='ym'>" + ET.tostring(mention_node) + "</hack>")
#             print "CV: DOING NEXT BRANCH " + ET.tostring(mention_node_redone)
#
#             accumulated_txt += accumulate_branch_text(mention_node_redone, mention_id_to_text_dict,
#                                                                                      mention_ent_id_to_ant_id_dict,
#                                                                                      is_sub=True)
#             ## NOW JUST ADD TAIL!!
#             print "*** Done with branch "
#         # else:
#         #     print " ** no more subs :" + str(mention_node.text)
#
#         # text AFTER this node but before sibling
#
#         accumulated_txt += mention_node.tail  # text after the node but before a sibling 761
#
#     return accumulated_txt



### ASSUME ROOT
# - get text before first mention
# - be sure last text after any mention (inc last) is grabbed as tail of that
# # - in between nodes will be the tail of the previous sibling!!
# def accumulate_all_text(original_root, mention_id_to_text_dict, mention_ent_id_to_ant_id_dict ):
#
#     # print " This should be original root :" + ET.tostring(original_root)
#     all_text = original_root.text # text before first subElement
#
#     all_text += accumulate_branch_text(original_root, mention_id_to_text_dict, mention_ent_id_to_ant_id_dict, is_sub=False)
#     # end_text = original_root.tail  ## SHOULD NOT BE!!  If this is doc node!
#
#     return all_text


def translate_entities_this_node(mention_node, accumulated_txt_from_child, entity_dict_of_lists):
    # entity_node = {}
    if mention_node.get('entity'):

        # ent_node = entity_dict_of_lists[mention_node.get('entity'))

        if mention_node.get('antecedent'):
            ##TRANSLATE by ADDINg the entity??!
            sub_term = give_substitute_term(mention_node.get('entity'), entity_dict_of_lists)
            accumulated_txt = strip_extra_white_space(mention_node.text) + ' { ' + sub_term + ' } ' + accumulated_txt_from_child
        else:
            print " >>>>> NO ANTECDANT for " + mention_node.text
            #  POssibly find another "alternative" representative of the entity . . just in case?
            if "text" in mention_node and strip_extra_white_space(mention_node.get("text")) in STD_PROFORMS:
                print " ENTITY IS PROFORM?  But is not ANTECDANT?? "

            accumulated_txt = strip_extra_white_space(mention_node.text) + accumulated_txt_from_child

    # translate just to text!!
    else:
        accumulated_txt = strip_extra_white_space(mention_node.text) + accumulated_txt_from_child



    # if mention_node.get('entity'):
    #     if mention_node.get('antecedent'):
    #         entity_node = {'antecedent': mention_node.get('antecedent'),
    #                        'entity': mention_node.get('entity')}
    #     else:
    #         entity_node = {'entity': mention_node.get('entity')}
    #
    #     entity_node['text'] = accumulated_txt # mention_node.text + accumulated_txt_from_child
    #
    #     print " >>> entity_node['text'] : " + entity_node['text']
    #
    #     if int(mention_node.get('entity')) in entity_dict_of_lists:
    #         entity_dict_of_lists[int(mention_node.get('entity'))].append(entity_node)
    #     else:
    #         entity_dict_of_lists[int(mention_node.get('entity'))] = [entity_node]

    return entity_dict_of_lists, accumulated_txt # entity_node['text']


def get_entities_this_node(mention_node, accumulated_txt_from_child, entity_dict_of_lists):
    entity_node = {}
    accumulated_txt = strip_extra_white_space(mention_node.text) + accumulated_txt_from_child
    if mention_node.get('entity'):
        if mention_node.get('antecedent'):
            entity_node = {'antecedent': mention_node.get('antecedent'),
                           'entity': mention_node.get('entity')}
        else:
            entity_node = {'entity': mention_node.get('entity')}

        entity_node['text'] = accumulated_txt # mention_node.text + accumulated_txt_from_child

        print " >>> entity_node['text'] : " + entity_node['text']

        if int(mention_node.get('entity')) in entity_dict_of_lists:
            entity_dict_of_lists[int(mention_node.get('entity'))].append(entity_node)
        else:
            entity_dict_of_lists[int(mention_node.get('entity'))] = [entity_node]

    return entity_dict_of_lists, accumulated_txt # entity_node['text']


def accumulate_branch_entities(root, entity_dict_of_lists, is_sub=False):
    search_node_str = 'mention'
    accumulated_txt_for_parent = ''

    for mention_node in root.findall(search_node_str):
        accumulated_txt_from_child = ''
        # Does it have children?
        if len(mention_node.findall('mention')) > 0:
            print "+++> would now do children: " + str(mention_node.text)

            entity_dict_of_lists, accumulated_txt_from_child = accumulate_branch_entities(mention_node, entity_dict_of_lists)

        # Convert this node
        entity_dict_of_lists, node_text = get_entities_this_node(mention_node, accumulated_txt_from_child, entity_dict_of_lists)
        accumulated_txt_for_parent += node_text

        ##CONFIRM!!!  seems to be?
        accumulated_txt_for_parent += mention_node.tail

    print "\n\n >> FINISHED one level : " + accumulated_txt_for_parent
    print " >> from : " + ET.tostring(root) + "\n\n"

    return entity_dict_of_lists, accumulated_txt_for_parent


def translate_branch_entities(root, entity_dict_of_lists, is_sub=False):
    search_node_str = 'mention'
    accumulated_txt_for_parent = ''

    for mention_node in root.findall(search_node_str):
        accumulated_txt_from_child = ''
        # Does it have children?
        if len(mention_node.findall('mention')) > 0:
            print "+++> would now do children: " + str(mention_node.text)

            accumulated_txt_from_child = translate_branch_entities(mention_node, entity_dict_of_lists)

        # Convert this node
        entity_dict_of_lists, node_text = translate_entities_this_node(mention_node, accumulated_txt_from_child, entity_dict_of_lists)
        accumulated_txt_for_parent += node_text

        ##CONFIRM!!!  seems to be?
        accumulated_txt_for_parent += mention_node.tail

    print "\n\n >> FINISHED one level : " + accumulated_txt_for_parent
    print " >> from : " + ET.tostring(root) + "\n\n"

    return accumulated_txt_for_parent


def get_entity_dict_of_lists(root):
    entity_dict_of_lists = {}
    return accumulate_branch_entities(root, entity_dict_of_lists)


def translate_proforms_and_to_text(root, entity_dict_of_lists):
    ## CAN we just take loop PLUS tail??
    return translate_branch_entities(root, entity_dict_of_lists)


def update_file(root, keep_proform=True):

    entity_dict_of_lists, accumulated_txt_for_parent = get_entity_dict_of_lists(root)

    print "======================\n\n THIS IS all nodes:"

    for ent_id, ent_list in entity_dict_of_lists.iteritems():
        print "===> ENTITY " + str(ent_id)
        for ent_node in ent_list:
            if "text" in ent_node and strip_extra_white_space(ent_node["text"]) in STD_PROFORMS:
                print " ENTITY IS PROFORM?"
            print " >> " + str(ent_node)

    new_text = strip_extra_white_space(translate_proforms_and_to_text(root, entity_dict_of_lists))

    print " >>> " + new_text




def update_file_old(root, keep_proform=True):

    mention_ant_ls = []
    mention_pro_ls = []

    mention_id_to_text_dict = {}
    mention_ent_id_to_ant_id_dict = {}

    # for atype in e.findall('type'):
    #     print(atype.get('foobar'))

    mention_id_to_text_dict, mention_ent_id_to_ant_id_dict = get_branch_data(root, mention_id_to_text_dict, mention_ent_id_to_ant_id_dict)

    print "******* have this many nodes in mention_id_to_text_dict: " + str(len(mention_id_to_text_dict))

    for ent_id, ent_str in mention_id_to_text_dict.iteritems():
        print str(ent_id) + " -> " + str(ent_str)

        #todo mention_ent_id_to_ant_id_dict is really just for debug???

    for ent_id, ant_id in mention_ent_id_to_ant_id_dict.iteritems():
        print " Looking for Ent with id: " + str(ent_id)


        if int(ent_id) in mention_id_to_text_dict:
            print ">> PROFORM: " + mention_id_to_text_dict[int(ent_id)]
        else:
            print " ERROR no " + str(ent_id) + " in mention_id_to_text_dict "

        if int(ant_id) in mention_id_to_text_dict:
            print ">> is ANTECEDANT: " + mention_id_to_text_dict[int(ant_id)]
        else:
            print " ERROR no " + str(ant_id) + " in mention_id_to_text_dict "


        # if mention_ent_id_to_ant_id_dict[ant_id] in mention_id_to_text_dict:
        #     print str(mention_id_to_text_dict[ant_id]) + " ==> " + mention_ent_id_to_ant_id_dict[int(ant_id)]  # still works?
        # else:
        #     print " ERROR no " + str(mention_ent_id_to_ant_id_dict[int(ant_id)]) + " in mention_id_to_text_dict "

    print ">>> NOW CONVERT ==============================> "

    converted_text = accumulate_all_text(root, mention_id_to_text_dict, mention_ent_id_to_ant_id_dict)

    print " RESULT : \n" + converted_text





def test_xml_node(node):

    print "> WHOLE NODE: " + ET.tostring(node)
    print "> tail NODE: " + node.tail
    print "> text NODE: " + node.text


def test_xml_lots(root):
    cnt = 0
    for mention_node in root.findall('mention'):
        test_xml_node(mention_node)

        if cnt > 10:
            return


def test_xml(file_name):
    file = ET.parse(file_name)
    root = file.getroot()
    update_file(root, keep_proform=True)
    # test_xml_lots(root)


''''

xml.etree.ElementTree.tostring(
xml.etree.ElementTree.tostringlist

'''


# test_xml('samples/out2_t1.xml')
# test_xml('samples/out2_t2.xml')
# test_xml('samples/out2_t3.xml')
# test_xml('samples/weirdTest.xml')
# test_xml('samples/out2.xml')
# test_xml('samples/out2.xml')
test_xml('samples/out4.xml')
# test_xml('samples/weirdTest.xml')

# print " now: " + strip_extra_white_space("jkhh    kjh k jh \n \n kgjhgj ")