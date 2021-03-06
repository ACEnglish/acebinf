"""
File for handling pedigree information
Family ID
Individual ID
Paternal ID
Maternal ID
Sex (1=male; 2=female; other=unknown)
Phenotype - See more at:
http://gatkforums.broadinstitute.org/gatk/discussion/7696/pedigree-ped-files
"""
from collections import defaultdict

# pylint: disable=too-few-public-methods


class Pedigree(dict):

    """
    Parses a pedigree file and allows different views
    """

    def __init__(self, file_name):
        super(Pedigree, self).__init__()
        self.samples = self.keys
        self.families = defaultdict(list)

        with open(file_name, 'r') as fh:
            for line in fh:
                if line.startswith("#"):
                    continue
                data = line.strip().split('\t')
                # check the data length
                n_ped = _PedSample(*data[:5], phenotype=data[5:])
                self.families[n_ped.fam_id].append(n_ped)
                if n_ped.ind_id in self:
                    raise KeyError("Duplicate Individual Id %s" % n_ped.ind_id)
                self[n_ped.ind_id] = n_ped

            # Give parents a presence in the ped, even if they didn't have a line
            for ind in self.values():
                if ind.pat_id not in self and ind.pat_id != "0":
                    self[ind.pat_id] = _PedSample(ind.fam_id, ind.pat_id, "0", "0", "1", "0")
                if ind.mat_id not in self and ind.mat_id != "0":
                    self[ind.mat_id] = _PedSample(ind.fam_id, ind.mat_id, "0", "0", "2", "0")
            # Set parent's offspring
            for n_ped in self.values():
                if n_ped.pat_id in self:
                    self[n_ped.pat_id].offspring.append(n_ped)
                    n_ped.father = self[n_ped.pat_id]
                if n_ped.mat_id in self:
                    self[n_ped.mat_id].offspring.append(n_ped)
                    n_ped.mother = self[n_ped.mat_id]

    def filter(self, inc_fam=None, exc_fam=None, inc_indiv=None, exc_indiv=None):
        """
        Exclude anything that's exc in the pedigree.
        Include only anything that's inc in the pedigree.
        """
        if inc_fam is not None:
            for i in self.keys():
                if self[i].fam_id not in inc_fam:
                    del self[i]
        if inc_indiv is not None:
            for i in self.keys():
                if self[i].ind_id not in inc_indiv:
                    del self[i]
        if exc_fam is not None:
            for i in self.keys():
                if self[i].fam_id in exc_fam:
                    del self[i]
        if exc_indiv is not None:
            for i in self.keys():
                if self[i].ind_id in exc_indiv:
                    del self[i]

    def all_male(self):
        """
        Returns all male individuals
        """
        for i in self:
            if self[i].sex == "1":
                yield self[i]

    def all_female(self):
        """
        Returns all female individuals
        """
        for i in self:
            if self[i].sex == "2":
                yield self[i]

    def all_affected(self):
        """
        Returns all affected individuals
        """
        for i in self:
            if self[i].phenotype == "2":
                yield self[i]

    def all_unaffected(self):
        """
        Returns all unaffected individuals
        """
        for i in self:
            if self[i].phenotype == "1":
                yield self[i]

    def get_siblings(self, indiv):
        """
        Returns the siblings of an individual
        """
        for i in self:
            if self[i].pat_id == self[indiv].pat_id or self[i].mat_id == self[indiv].mat_id:
                yield self[i]

    def get_trio_probands(self):
        """
        Yields _PedSample probands that are part of a trio i.e. niether parent is 0
        """
        for indiv in self.values():
            if indiv.mat_id != '0'and indiv.pat_id != '0':
                yield indiv

    def get_quad_probands(self):
        """
        Yields _PedSample proband tuples that are part of an exact quad.
        """
        for fam in self.families:
            already_yielded = {}
            for indiv in self.families[fam]:
                if indiv.ind_id in already_yielded:
                    continue
                if indiv.mat_id != "0" and indiv.pat_id != "0":
                    siblings = set(self[indiv.mat_id].offspring).intersection(set(self[indiv.pat_id].offspring))
                    if len(siblings) == 2:
                        yield list(siblings)
                    for sib in siblings:
                        if indiv != sib:
                            already_yielded[sib.ind_id] = 1
                            yield (indiv, sib)


class _PedSample(object):

    """
    An individual in a pedigree
    Family ID
    Individual ID
    Paternal ID
    Maternal ID
    Sex (1=male; 2=female; other=unknown)
    Phenotype
    """

    def __init__(self, fam_id, ind_id, pat_id, mat_id, sex, phenotype):
        self.fam_id = fam_id
        self.ind_id = ind_id
        self.pat_id = pat_id
        self.mat_id = mat_id
        self.sex = sex
        self.phenotype = phenotype
        self.father = None
        self.mother = None
        self.offspring = []

    def __hash__(self):
        return hash(self.ind_id)

    def __repr__(self):
        return "PedigreeSample<%s:%s %s>" % (self.fam_id, self.ind_id, self.sex)

    def __str__(self):
        return "\t".join([self.fam_id, self.ind_id, self.pat_id,
                          self.mat_id, self.pat_id, self.sex,
                          "\t".join(self.phenotype)])
