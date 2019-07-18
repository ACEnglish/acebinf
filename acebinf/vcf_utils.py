"""
little methods for editing pyvcf format/info fields
"""

import vcf
import pysam
from collections import OrderedDict

class VCFEntry():

    def __init__(self, entry):
        self.__orig_entry = entry
        for attr in dir(entry):
            if attr.startswith("_"): continue
            setattr(self, attr, getattr(entry, attr))
        self.samples = OrderedDict()
        self.info = dict(entry.info)
        tlens = self.get_type_lens()
        ml = max(tlens[1])
        if ml >= 25:
            self.info["END"] = self.start + ml
        for key in entry.samples:
            samp = {}
            for fmt in entry.samples[key]:
                if isinstance(entry.samples[key][fmt], tuple) or isinstance(entry.samples[key][fmt], list) :
                    samp[fmt] = [x if x != None else "." for x in entry.samples[key][fmt] ]
                else:
                    samp[fmt] = entry.samples[key][fmt] if entry.samples[key][fmt] is not None else '.'
            gt = samp["GT"]
            while len(gt) < 2:
                gt.append(".")
            self.samples[key] = samp
            self.samples[key]["GT"] = "{0}/{1}".format(*gt)

    def get_type_lens(self):
        """
        Parse an entry and return it's sv_type and it's sv_len
        """
        mREF = self.ref
        # TODO - should get the longest?
        mALTs = self.alts
        sv_types = []
        sv_lens = []
        # Get type for counting - MYTYPES
        for mALT in mALTs:
            if len(mREF) == len(mALT):
                sv_types.append("REPL")
                sv_lens.append(len(mREF))
            elif len(mREF) == 1:
                sv_types.append("INS")
                sv_lens.append(len(mALT) - 1)
            elif len(mALT) == 1:
                sv_types.append("DEL")
                sv_lens.append(len(mREF) - 1)
            elif len(mREF) > len(mALT):
                sv_types.append("SUBSDEL")
                sv_lens.append(len(mREF) - len(mALT))
            elif len(mALT) > len(mREF):
                sv_types.append("SUBSINS")
                sv_lens.append(len(mALT) - len(mREF))
            else:
                logging.error(str(entry))
                logging.error("shouldn't have some new crazy type\n")
                exit()

        return sv_types, sv_lens


    def __str__(self):
        """
        tostring
        """
        info = ";".join(['%s=%s' % (x,str(y)) for x,y in self.info.items()])
        fmt = ":".join(self.format)
        filt = ";".join([x for x in self.filter])
        sampstr = []
        def f(i):
            if isinstance(i, tuple) or isinstance(i, list):
                return ",".join(str(x) for x in i)
            return str(i)
        for samp in self.samples.values():
            sampstr.append(":".join([f(x) for x in samp.values()]))
        sampstr = "\t".join(sampstr)

        alt = ",".join(x for x in self.alts)
        # Problem with INFO/END ... reserved attribute
        return f"{self.chrom}\t{self.pos}\t{self.id if self.id is not None else '.'}\t{self.ref}\t{alt}\t{self.qual}\t{filt}\t{info}\t{fmt}\t{sampstr}"


def add_format(vcf_file, nid, num, ntype, desc):
    """
    In-place addition of a new FORMAT into the vcf_file
    """
    # pylint: disable=protected-access
    vcf_file.formats[nid] = vcf.parser._Format(id=nid, num=num, type=ntype, desc=desc)


def add_info(vcf_file, nid, num, ntype, desc, source=None, version=None):
    """
    In-place addition of a new INFO into the vcf_file
    """
    # pylint: disable=protected-access
    vcf_file.infos[nid] = vcf.parser._Info(
        id=nid, num=num, type=ntype, desc=desc, source=source, version=version)


def edit_format(vcf_entry, sample, **kwargs):
    """
    Given a sample and FORMAT=value kwargs, edit an entry's information in-place
    """
    fmt_data = vcf_entry.FORMAT.split(':')
    for key in kwargs:
        if key not in fmt_data:
            vcf_entry.add_format(key)

    n_call_data = vcf.model.make_calldata_tuple(sample.data._fields + tuple(kwargs.keys()))
    n_data = tuple(kwargs.values())
    sample.data += n_data
    sample.data = n_call_data(*sample.data)
