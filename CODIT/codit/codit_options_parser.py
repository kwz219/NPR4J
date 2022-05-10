import argparse

import onmt


def get_structure_transformation_parser():
    parser_structure = argparse.ArgumentParser(
        description='full_translation.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    onmt.opts.add_md_help_argument(parser_structure)
    onmt.opts.translate_opts(parser_structure)
    parser_structure.add_argument('--grammar', help='Path of the grammar file', required=True)
    parser_structure.add_argument('--tmp_file', default='tmp/generated_node_types.nt')
    return parser_structure


def get_token_transformation_parser():
    parser = argparse.ArgumentParser(
        description='translate_token.py',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    onmt.opts.add_md_help_argument(parser)
    onmt.opts.translate_opts(parser)
    parser.add_argument('--name', help='Name of the Experiment')
    parser.add_argument('--tmp_file', default='')
    parser.add_argument('--grammar', required=True)
    parser.add_argument('--atc', default=None)
    parser.add_argument('--tree_count', type=int, default=2)
    return parser


def get_options(options):
    if options.cout is None:
        options.cout = 'tmp/' + options.name + '.gen.rule'
    if 'prev' in options.src_struct:
        tgt_struct = options.src_struct.replace('prev', 'next')
    else:
        tgt_struct = None
    structure_options = get_structure_transformation_parser().parse_args(
        (' -src ' + options.src_struct + ' -batch_size 32'
         + ' -model ' + options.model_structure + ' -beam_size 10 -n_best 5 '
         + ' --grammar ' + options.grammar + ' --tmp_file tmp/' + options.cout
         + ((' -tgt ' + tgt_struct) if tgt_struct is not None else '')
         ).split())

    token_options = get_token_transformation_parser().parse_args(
        ('-gpu 0 -model ' + options.model_token + ' -src ' + options.src_token + ' -tgt ' + options.tgt_token
         + ' --name ' + options.name + '.' + options.tree_count + ' -batch_size 1 ' + ' -beam_size ' + str(options.beam_size)
         + ' -n_best ' + str(options.n_best) + ' --tmp_file tmp/' + options.cout
         + ' --atc ' + options.atc + ' --grammar ' + options.grammar + ' --tree_count ' + options.tree_count
         # + ' -verbose '
         ).split())
    return structure_options, token_options
