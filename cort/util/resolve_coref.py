
from cort_wrapper import call_cort
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
# http://stackoverflow.com/questions/10408927/how-to-get-all-sub-elements-of-an-element-tree-with-python-elementtree

# def resolve_coref(text_blog):
#
#     xml_resolutions = call_cort(text_blog)
#
#     root = ET.fromstring(xml_resolutions)

def add_to_dicts(mention_node, mention_id_dict, mention_ant_id_dict, mention_ant_str_dict):
    print " text :" + str(mention_node.text)
    # print " text " + str(mention_node.dump('text'))
    # dump
    if (mention_node.get('id')):
        mention_id_dict[mention_node.get('id')] = mention_node.text

        if (mention_node.get('antecedent')):
            mention_ant_id_dict[mention_node.get('id')] = mention_node.get('antecedent')
            mention_ant_str_dict[mention_node.get('id')] = mention_node.text

    return mention_id_dict, mention_ant_id_dict, mention_ant_str_dict


def get_branch_data(root, mention_id_dict, mention_ant_id_dict, mention_ant_str_dict, is_sub=False):
    if is_sub:
        search_node_str = './/mention/mention'
    else:
        search_node_str = 'mention'


    if len(root.findall(search_node_str)) == 0:
        print str(is_sub) + "-------------> how is this zero? " + ET.tostring(root)
    else:
        print str(is_sub) + "---> do have: " + str(len(root.findall(search_node_str))) + " | " + ET.tostring(root)


    for mention_node in root.findall(search_node_str):


        # if (mention_node.get('entity')):
        #     print " ENTITY "
        mention_id_dict, mention_ant_id_dict, mention_ant_str_dict = add_to_dicts(mention_node,
                                                                                    mention_id_dict,
                                                                                  mention_ant_id_dict,
                                                                                  mention_ant_str_dict)
        if len(mention_node.findall('mention')) > 0:

            # todo maybe reparse?  but from string? ET.parse(file_name)
            mention_node_redone = ET.fromstring("<hack entity='ym'>" + ET.tostring(mention_node) + "</hack>")
            print "DOING NEXT BRANCH " + ET.tostring(mention_node_redone)
            mention_id_dict, mention_ant_id_dict, mention_ant_str_dict = get_branch_data(mention_node_redone, mention_id_dict,
                                                                                         mention_ant_id_dict,
                                                                                         mention_ant_str_dict,
                                                                                         is_sub=True)
            print "*** Done with branch "
        else:
            print " ** no more subs :" + str(mention_node.text)
        # else:
        #     print " no entity? mention_node: " + ET.tostring(mention_node)

    return mention_id_dict, mention_ant_id_dict, mention_ant_str_dict


## CONVERT text and Add TAIL!!!
def convert_text_this_node(this_node, mention_id_dict, mention_ant_id_dict, mention_ant_str_dict):
    node_text = ''
    if this_node.get('id'):

        if this_node.get('antecedent'):
            print ">> PROFORM:  "  + this_node.text
            print ">> LOOKING FOR antecedant " + this_node.get('antecedent')
            print ">> FOUND: " + mention_id_dict[mention_ant_id_dict[this_node.get('antecedent')]]

            # print str(mention_ant_str_dict[this_node.get('antecedent')]) + " ==> " + mention_id_dict[mention_ant_id_dict[this_node.get('antecedent')]]

            node_text += this_node.text + mention_id_dict[mention_ant_id_dict[this_node.get('antecedent')]] #todo add a seperator?

    else:
        print " NO id?? " + ET.tostring(this_node)



    return node_text



# TODO: use OOD to encapsulate and stop passing the dicts
## MAYBE return node just done then does remove(subelement)
# CURRENTLY this is "get all data from all nodes" but not the content itself of this node TODO: rethink
def accumulate_branch_text(root, mention_id_dict, mention_ant_id_dict, mention_ant_str_dict, is_sub=False):
    if is_sub:
        search_node_str = './/mention/mention'  ## THIS IS SO HACKY TODO: refrain from embracing evil
    else:
        search_node_str = 'mention'

    # treat each node the same and return that inner awesome translated
    accumulated_txt = ''

    for mention_node in root.findall(search_node_str):
        # Convert this node
        accumulated_txt += convert_text_this_node(mention_node, mention_id_dict, mention_ant_id_dict,
                                                  mention_ant_str_dict)
        # Does it have children?
        if len(mention_node.findall('mention')) > 0:

            # INNER MENTION!!
            # todo maybe reparse?  but from string? ET.parse(file_name)
            mention_node_redone = ET.fromstring("<hack entity='ym'>" + ET.tostring(mention_node) + "</hack>")
            print "CV: DOING NEXT BRANCH " + ET.tostring(mention_node_redone)

            accumulated_txt += accumulate_branch_text(mention_node_redone, mention_id_dict,
                                                                                     mention_ant_id_dict,
                                                                                     mention_ant_str_dict,
                                                                                     is_sub=True)
            ## NOW JUST ADD TAIL!!


            print "*** Done with branch "
        # else:
        #     print " ** no more subs :" + str(mention_node.text)

        # text AFTER this node but before sibling
        accumulated_txt += mention_node.tail  # text after the node but before a sibling

    return accumulated_txt



### ASSUME ROOT
# - get text before first mention
# - be sure last text after any mention (inc last) is grabbed as tail of that
# - in between nodes will be the tail of the previous sibling!!
def accumulate_all_text(original_root, mention_id_dict, mention_ant_id_dict, mention_ant_str_dict ):

    # print " This should be original root :" + ET.tostring(original_root)
    all_text = original_root.text # text before first subElement

    all_text += accumulate_branch_text(original_root, mention_id_dict, mention_ant_id_dict, mention_ant_str_dict, is_sub=False)
    # end_text = original_root.tail  ## SHOULD NOT BE!!  If this is doc node!

    return all_text



def update_file(root, keep_proform=True):

    mention_ant_ls = []
    mention_pro_ls = []

    mention_id_dict = {}
    mention_ant_id_dict = {}
    mention_ant_str_dict = {}

    # for atype in e.findall('type'):
    #     print(atype.get('foobar'))

    mention_id_dict, mention_ant_id_dict, mention_ant_str_dict = get_branch_data(root, mention_id_dict, mention_ant_id_dict, mention_ant_str_dict)



    for ent_id, ent_str in mention_id_dict.iteritems():
        print str(ent_id) + " -> " + str(ent_str)

    for ant_id, ent_id in mention_ant_id_dict.iteritems():
        print " Looking for Ent with id: " + str(mention_ant_id_dict[ant_id])
        if mention_ant_id_dict[ant_id] in mention_id_dict:
            print str(mention_ant_str_dict[ant_id]) + " ==> " + mention_id_dict[mention_ant_id_dict[ant_id]]
        else:
            print " ERROR no " + str(mention_ant_id_dict[ant_id]) + " in mention_id_dict "

    print ">>> NOW CONVERT ==============================> "

    converted_text = accumulate_all_text(root, mention_id_dict, mention_ant_id_dict, mention_ant_str_dict)

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

# test_xml('samples/out2.xml')
test_xml('samples/out4.xml')
# test_xml('samples/weirdTest.xml')