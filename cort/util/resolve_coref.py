
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


def do_branch(root, mention_id_dict, mention_ant_id_dict, mention_ant_str_dict, is_sub=False):
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
            mention_id_dict, mention_ant_id_dict, mention_ant_str_dict = do_branch(mention_node_redone, mention_id_dict,
                                                                                    mention_ant_id_dict,
                                                                                    mention_ant_str_dict,
                                                                                    is_sub=True)
            print "*** Done with branch "
        else:
            print " ** no more subs :" + str(mention_node.text)
        # else:
        #     print " no entity? mention_node: " + ET.tostring(mention_node)

    return mention_id_dict, mention_ant_id_dict, mention_ant_str_dict


def update_file(root):

    mention_ant_ls = []
    mention_pro_ls = []

    mention_id_dict = {}
    mention_ant_id_dict = {}
    mention_ant_str_dict = {}

    # for atype in e.findall('type'):
    #     print(atype.get('foobar'))

    mention_id_dict, mention_ant_id_dict, mention_ant_str_dict = do_branch(root, mention_id_dict, mention_ant_id_dict, mention_ant_str_dict)

    for ent_id, ent_str in mention_id_dict.iteritems():
        print str(ent_id) + " -> " + str(ent_str)

    for ant_id, ent_id in mention_ant_id_dict.iteritems():
        print " Looking for Ent with id: " + str(mention_ant_id_dict[ant_id])
        if mention_ant_id_dict[ant_id] in mention_id_dict:
            print str(mention_ant_str_dict[ant_id]) + " ==> " + mention_id_dict[mention_ant_id_dict[ant_id]]
        else:
            print " ERROR no " + str(mention_ant_id_dict[ant_id]) + " in mention_id_dict "

















def test_xml(file_name):
    file = ET.parse(file_name)
    root = file.getroot()
    update_file(root)



''''

xml.etree.ElementTree.tostring(
xml.etree.ElementTree.tostringlist

'''

test_xml('samples/out2.xml')