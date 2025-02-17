import pytest
import networkx as nx
from cgsmiles import MoleculeResolver
from cgsmiles.resolve import generate_edge

@pytest.mark.parametrize('bonds_source, bonds_target, edge, btypes',(
                        # single bond source each
                        ({0: ["$"]},
                         {3: ["$"]},
                         (0, 3),
                         ('$', '$')),
                        # include a None
                        ({0: ["$"], 1: []},
                         {3: ["$"]},
                         (0, 3),
                         ('$', '$')),
                        # multiple sources one match
                        ({0: ['$1'], 2: ['$2']},
                         {1: ['$2'], 3: ['$']},
                         (2, 1),
                         ('$2', '$2')),
                        # left right selective bonding
                        ({0: ['$'], 1: ['>'], 3: ['<']},
                         {0: ['>'], 1: ['$5']},
                         (3, 0),
                         ('<', '>')),
                        # left right selective bonding
                        # with identifier
                        ({0: ['$'], 1: ['>'], 3: ['<1']},
                         {0: ['>'], 1: ['$5'], 2: ['>1']},
                         (3, 2),
                         ('<1', '>1')),

))
def test_generate_edge(bonds_source, bonds_target, edge, btypes):
    source = nx.path_graph(5)
    target = nx.path_graph(4)
    nx.set_node_attributes(source, bonds_source, "bonding")
    nx.set_node_attributes(target, bonds_target, "bonding")
    new_edge, new_btypes = generate_edge(source, target, bond_attribute="bonding")
    assert new_edge == edge
    assert new_btypes == btypes


@pytest.mark.parametrize('smile, ref_nodes, ref_edges',(
                        # smiple linear seqeunce
                        ("{[#OHter][#PEO]|2[#OHter]}.{#PEO=[$]COC[$],#OHter=[$][O]}",
                        #           0 1             2 3 4 5 6 7 8
                        [('OHter', 'O H'), ('PEO', 'C O C H H H H'),
                        #        9 10 11 12 13 14 15         16 17
                         ('PEO', 'C O C H H H H'), ('OHter', 'O H')],
                        [(0, 1), (0, 2), (2, 3), (3, 4), (2, 5), (2, 6), (4, 7),
                         (4, 8), (4, 9), (9, 10), (10, 11), (9, 12), (9, 13),
                         (11, 14), (11, 15), (11, 16), (16, 17)]),
                        # smiple linear seqeunce unconsumed bonding descrpt
                        ("{[#OHter][#PEO]|2[#OHter]}.{#PEO=[$]CO[>]C[$],#OHter=[$][O]}",
                        #           0 1             2 3 4 5 6 7 8
                        [('OHter', 'O H'), ('PEO', 'C O C H H H H'),
                        #        9 10 11 12 13 14 15         16 17
                         ('PEO', 'C O C H H H H'), ('OHter', 'O H')],
                        [(0, 1), (0, 2), (2, 3), (3, 4), (2, 5), (2, 6), (4, 7),
                         (4, 8), (4, 9), (9, 10), (10, 11), (9, 12), (9, 13),
                         (11, 14), (11, 15), (11, 16), (16, 17)]),
                        # smiple linear seqeunce with ionic bond
                        ("{[#OHter][#PEO]|2[#OHter]}.{#PEO=[$]COC[$],#OHter=[$][O-].[Na+]}",
                        #           0 1             2 3 4 5 6 7 8
                        [('OHter', 'O Na'), ('PEO', 'C O C H H H H'),
                        #        9 10 11 12 13 14 15         16 17
                         ('PEO', 'C O C H H H H'), ('OHter', 'O Na')],
                        [(0, 1), (0, 2), (2, 3), (3, 4), (2, 5), (2, 6), (4, 7),
                         (4, 8), (4, 9), (9, 10), (10, 11), (9, 12), (9, 13),
                         (11, 14), (11, 15), (11, 16), (16, 17)]),

                        # uncomsumed bonding IDs; note that this is not the same
                        # molecule as previous test case. Here one of the OH branches
                        # and replaces an CH2 group with CH-OH
                        ("{[#OHter][#PEO]|2[#OHter]}.{#PEO=[>][$1]COC[<],#OHter=[$1][O]}",
                        [('OHter', 'O H'), ('PEO', 'C O C H H H H'),
                         ('PEO', 'C O C H H H H'), ('OHter', 'O H')],
                        [(0, 1), (0, 2), (2, 3), (2, 5), (2, 10), (3, 4),
                         (4, 6), (4, 7), (4, 17), (8, 9), (8, 11), (8, 14),
                         (8, 18), (9, 10), (10, 12), (10, 13), (14, 15)]),
                        # simple branched sequence
                        ("{[#Hter][#PE]([#PEO][#Hter])[#PE]([#PEO][#Hter])[#Hter]}.{#Hter=[$]H,#PE=[$]CC[$][$],#PEO=[$]COC[$]}",
                        [('Hter', 'H'), ('PE', 'C C H H H'), ('PEO', 'C O C H H H H'), ('Hter', 'H'),
                         ('PE', 'C C H H H'), ('PEO', 'C O C H H H H'), ('Hter', 'H'), ('Hter', 'H')],
                        [(0, 1), (1, 2), (1, 3), (1, 4), (2, 5), (2, 6), (2, 14), (6, 7), (6, 9), (6, 10), (7, 8),
                         (8, 11), (8, 12), (8, 13), (14, 15), (14, 16), (14, 17), (15, 18), (15, 19), (15, 27),
                         (19, 20), (19, 22), (19, 23), (20, 21), (21, 24), (21, 25), (21, 26)]),
                        # something with a ring
                        #            012 34567
                        #            890123456
                        ("{[#Hter][#PS]|2[#Hter]}.{#PS=[$]CC[$]c1ccccc1,#Hter=[$]H}",
                        [('Hter', 'H'), ('PS', 'C C C C C C C C H H H H H H H H'),
                         ('PS', 'C C C C C C C C H H H H H H H H'), ('Hter', 'H')],
                        [(0, 1), (1, 2), (1, 9), (1, 10), (2, 3), (2, 11), (2, 17),
                         (3, 4), (3, 8), (4, 5), (4, 12), (5, 6), (5, 13), (6, 7),
                         (6, 14), (7, 8), (7, 15), (8, 16), (17, 18), (17, 25),
                         (17, 26), (18, 19), (18, 27), (18, 33), (19, 20), (19, 24),
                         (20, 21), (20, 28), (21, 22), (21, 29), (22, 23), (22, 30),
                         (23, 24), (23, 31), (24, 32)]),
                        # something more complicated branched
                        # here we have multiple bonding descriptors
#                       # despite being the same residue we have 3 fragments after adding hydrgens
#                       ("{[#PE][#PE]([#PE][#PE])[#PE][#PE]([#PE][#PE])[#PE]}.{#PE=[<][<]CC[>][>]}",
#                       [('PE', 'C C H H H H H'), ('PE', 'C C H H H'), ('PE', 'C C H H H H'),
#                        ('PE', 'C C H H H H H'), ('PE', 'C C H H H H'), ('PE', 'C C H H H'),
#                        ('PE', 'C C H H H H'), ('PE', 'C C H H H H H'), ('PE', 'C C H H H H H')]
#                       [,
#                        (

))
def test_def_big_smile_parser(smile, ref_nodes, ref_edges):
    meta_mol, molecule = MoleculeResolver(smile).resolve()
#    nx.draw_networkx(meta_mol.molecule, with_labels=True, labels=nx.get_node_attributes(meta_mol.molecule, 'element'))
#    plt.show()
    for node, ref in zip(meta_mol.nodes, ref_nodes):
        assert meta_mol.nodes[node]['fragname'] ==  ref[0]
        block_graph = meta_mol.nodes[node]['graph']
        elements = nx.get_node_attributes(block_graph, 'element') #.values())
        sorted_elements =  [elements[key] for key in sorted(elements)]
        assert sorted_elements == ref[1].split()
    assert sorted(molecule.edges) == sorted(ref_edges)
