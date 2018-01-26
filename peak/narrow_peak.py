from lib_utils import *

import sys


class NarrowPeak:
    """ The object of this class represents one entry of a file that has narrow peaks BED format """
    def __init__(self):
        self.chrID = None
        self.start = 0
        self.end = 0

        # following attributes will be string because of the bed files after merged.
        self.name = '.'
        self.score = '0'
        self.strand = '.'
        self.sig_val = '0.0'
        self.p_val = '-1.0'
        self.q_val = '-1.0'
        self.point_src = '-1'

        """ attributes for gene-based annotation of the peak """
        self.genic_region_to_size = {}

        """ attributes for seeing a distribution of variants """
        self.var_pos_to_cnt = {}  # positions of variants (0-based) to their counts
        self.var_pos_to_genic_region = {}

    # END: __init__

    def __str__(self):
        return '%s\t%d\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % \
               (self.chrID, self.start, self.end, self.name, self.score,
                self.strand, self.sig_val, self.p_val, self.q_val, self.point_src)

    # END: __str__

    def get_position(self):
        """
        :return: a tuple (start, end)
        """
        return self.start, self.end

    # END: the function 'get_position'

    def get_genic_region_to_size(self):
        """
        :return: a dictionary that documents the size of each genic region on this peak.
                 (key: a genic region, value: a size of the genic region (integer))
        """
        return self.genic_region_to_size

    # END: the function 'get_genic_region_to_size'

    def get_genic_region_to_var_cnt(self):
        """
        :return: a dictionary that documents the number of variants of each genic region on this peak.
                 (key: a genic region, value: the number of variants on the genic region (integer))
        """

        genic_region_to_var_cnt = {}

        for pos in self.var_pos_to_cnt:
            var_cnt = self.var_pos_to_cnt[pos]
            var_genic_region = self.var_pos_to_genic_region[pos]

            if var_genic_region not in genic_region_to_var_cnt:
                genic_region_to_var_cnt[var_genic_region] = 0

            genic_region_to_var_cnt[var_genic_region] += var_cnt

        return genic_region_to_var_cnt

    # END: the function 'get_genic_region_to_var_cnt'

    @staticmethod
    def parse_peak_file(peak_filename):
        """
        :param peak_filename: a file which has a narrow peak bed format
        :return: a list of NarrowPeak objects
        """
        # File Format:
        # Column:        0       | 1         | 2        | 3               | 4      | 5       |
        # ID:            ChrID   | start     | end      | name            | score  | strand  |
        # Example:       chr14   | 56879239  | 56879435 | ILF3_K562_rep02 | 1000   | -       |
        # Column:        6            | 7         | 8        | 9
        # ID:            signal_value | p-value   | q-value  | point_src
        # Example:       1.29065      | 0.198802  | -1       | -1

        peak_file = open(peak_filename, 'r')

        peak_list = []

        for line in peak_file.readlines():
            peak = NarrowPeak()
            peak.parse_peak_entry(line.strip())
            peak_list.append(peak)

        peak_file.close()

        return peak_list

    # END: the function 'parse_peak_file'

    def parse_peak_entry(self, peak_entry):
        """
        :param peak_entry: an entry from a narrow peak bed file
        """

        fields = peak_entry.split('\t')

        self.chrID = fields[0]
        self.start = int(fields[1])
        self.end = int(fields[2])
        self.name = fields[3]
        self.score = fields[4]
        self.strand = fields[5]
        self.sig_val = fields[6]
        self.p_val = fields[7]
        self.q_val = fields[8]
        self.point_src = fields[9]

    # END: the function 'parse_peak_entry'

    def set_genic_region_stat(self, region_code_list):
        """
        This code makes up the 'genic_region_to_size' attribute.

        :param region_code_list: a list that has a same length with the peak and
                                 consists of codes representing each genic region
                                 (100, 101, ..., 107)

        ** codes for each genic region **
        100: ORF
        101: 5UTR
        102: 3UTR
        103: UTR (both 5UTR and 3UTR)
        104: ncRNA exonic
        105: intronic
        106: ncRNA intronic
        107: intergenic
        """
        code_to_region = {100: 'ORF', 101: '5UTR', 102: '3UTR', 103: 'UTR', 104: 'ncRNA_exonic',
                          105: 'intronic', 106: 'ncRNA_intronic', 107: 'intergenic'}

        # make a statistics for genic regions
        for code in region_code_list:
            try:
                genic_region = code_to_region[code]
            except KeyError:
                print('Error in %s: invalid code for genic region' % caller_file_and_line())
                sys.exit()

            if genic_region not in self.genic_region_to_size:
                self.genic_region_to_size[genic_region] = 0

            self.genic_region_to_size[genic_region] += 1

    # END: the function 'set_genic_region_stat'

    def record_variant(self, variant):
        """
        :param variant: an object of the class 'VCFData'
        """

        assert variant.__class__.__name__ == 'VCFData'
        assert self.start <= (variant.pos - 1) < self.end

        var_pos = variant.pos - 1  # 1-based -> 0-based

        if var_pos not in self.var_pos_to_cnt:
            self.var_pos_to_cnt[var_pos] = 0

        self.var_pos_to_cnt[var_pos] += 1

        if var_pos not in self.var_pos_to_genic_region:
            self.var_pos_to_genic_region[var_pos] = variant.get_var_genic_region()
        else:
            assert self.var_pos_to_genic_region[var_pos] == variant.get_var_genic_region()

    # END: the function 'record_variant'
# END: the definition of the class 'NarrowPeak'