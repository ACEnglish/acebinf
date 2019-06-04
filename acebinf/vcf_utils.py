"""
little methods for editing pyvcf format/info fields
"""

import vcf


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
