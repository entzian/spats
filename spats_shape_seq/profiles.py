
import math
from spats_shape_seq.mask import PLUS_PLACEHOLDER, MINUS_PLACEHOLDER


class Profiles(object):

    def __init__(self, targets, run, counters):
        self._targets = targets
        self._counters = counters
        self._cotrans = run.cotrans
        self._run = run
        self.masks = self._run.masks
        for m in self.masks:
            if m:
                break
        else:
            self.masks = [ PLUS_PLACEHOLDER, MINUS_PLACEHOLDER ]

        profiles = {}
        for target in self._targets.targets:
            n = len(target.seq)
            if run.cotrans:
                for end in range(run.cotrans_minimum_length, n + 1):
                    profiles["{}_{}".format(target.name, end)] = self._createProfile(target, end)
            else:
                p = self._createProfile(target, n)
                if run.allow_multiple_rt_starts:
                    # We need to "stitch together" stats from all ends...
                    for end in range(n):
                        self._addToProfile(p, target, end)
                profiles[target.name] = p
        self._profiles = profiles

    def _createProfile(self, target, end):
        counters = self._counters
        tp = TargetProfiles(self, target,
                            counters.mask_counts(target, self.masks[0], end),
                            counters.mask_counts(target, self.masks[1], end),
                            counters.mask_depths(target, self.masks[0], end),
                            counters.mask_depths(target, self.masks[1], end),
                            counters.mask_quality_depths(target, self.masks[0], end),
                            counters.mask_quality_depths(target, self.masks[1], end))
        if self._run.count_mutations:
            tp.treated_muts = counters.mask_muts(target, self.masks[0], end)
            tp.untreated_muts = counters.mask_muts(target, self.masks[1], end)
            tp.treated_edge_muts = counters.mask_edge_muts(target, self.masks[0], end)
            tp.untreated_edge_muts = counters.mask_edge_muts(target, self.masks[1], end)
            tp.treated_removed_muts = counters.mask_removed_muts(target, self.masks[0], end)
            tp.untreated_removed_muts = counters.mask_removed_muts(target, self.masks[1], end)
        if self._run.handle_indels:
            tp.treated_inserts = counters.mask_inserts(target, self.masks[0], end)
            tp.untreated_inserts = counters.mask_inserts(target, self.masks[1], end)
            tp.treated_deletes = counters.mask_deletes(target, self.masks[0], end)
            tp.untreated_deletes = counters.mask_deletes(target, self.masks[1], end)
        return tp

    @staticmethod
    def _addToVect(vect, vtoadd, extend = False):
        overlapped = min(len(vect), len(vtoadd))
        for i in range(overlapped):
            vect[i] += vtoadd[i]
        if len(vtoadd) > len(vect):
            vect += [0] * (len(vtoadd) - len(vect))
            for i in range(overlapped, len(vtoadd)):
                vect[i] += vtoadd[i]

    def _addToProfile(self, p, target, end):
        counters = self._counters
        # TAI:  the following is ugly.  refactor....
        Profiles._addToVect(p.treated_counts, counters.mask_counts(target, self.masks[0], end))
        Profiles._addToVect(p.untreated_counts, counters.mask_counts(target, self.masks[1], end))
        Profiles._addToVect(p.treated_depths, counters.mask_depths(target, self.masks[0], end))
        Profiles._addToVect(p.untreated_depths, counters.mask_depths(target, self.masks[1], end))
        Profiles._addToVect(p.treated_quality_depths, counters.mask_quality_depths(target, self.masks[0], end))
        Profiles._addToVect(p.untreated_quality_depths, counters.mask_quality_depths(target, self.masks[1], end))
        if self._run.count_mutations:
            Profiles._addToVect(p.treated_muts, counters.mask_muts(target, self.masks[0], end))
            Profiles._addToVect(p.untreated_muts, counters.mask_muts(target, self.masks[1], end))
            Profiles._addToVect(p.treated_edge_muts, counters.mask_edge_muts(target, self.masks[0], end))
            Profiles._addToVect(p.untreated_edge_muts, counters.mask_edge_muts(target, self.masks[1], end))
            Profiles._addToVect(p.treated_removed_muts, counters.mask_removed_muts(target, self.masks[0], end))
            Profiles._addToVect(p.untreated_edge_muts, counters.mask_removed_muts(target, self.masks[1], end))
        if self._run.handle_indels:
            Profiles._addToVect(p.treated_inserts, counters.mask_inserts(target, self.masks[0], end))
            Profiles._addToVect(p.untreated_inserts, counters.mask_inserts(target, self.masks[1], end))
            Profiles._addToVect(p.treated_deletes, counters.mask_deletes(target, self.masks[0], end))
            Profiles._addToVect(p.untreated_deletes, counters.mask_deletes(target, self.masks[1], end))

    def profilesForTarget(self, target):
        return self._profiles[target.name]

    def profilesForTargetNamed(self, target_name):
        return self._profiles[target_name]

    def profilesForTargetAndEnd(self, target_name, end):
        if self._cotrans:
            return self._profiles["{}_{}".format(target_name, end)]
        else:
            return self._profiles[target_name]

    def compute(self):
        for profile in self._profiles.values():
            profile.compute()

    def write(self, target_path):
        with open(target_path, 'wb') as outfile:
            outfile.write('sequence\trt_start\tfive_prime_offset\tnucleotide\ttreated_mods\tuntreated_mods\tbeta\ttheta\tc\n')
            for key in sorted(self._profiles.keys()):
                self._profiles[key].write(outfile)

    def cotrans_data(self):
        if self._cotrans:
            return [ (int(key.split('_')[-1]), prof.data()) for key, prof in iter(self._profiles.items()) ]
        else:
            return [ (len(prof.data()["t"]) - 1, prof.data()) for key, prof in iter(self._profiles.items()) ]

    def cotrans_keys(self):
        return sorted(self._profiles.keys(), key = lambda x : int(x.split('_')[-1]))

    def data_range(self, data_type):
        vmin = None
        vmax = None
        for profile in self._profiles.values():
            vals = getattr(profile, data_type)
            vmin = min(vals) if vmin is None else min(min(vals), vmin)
            vmax = max(vals) if vmax is None else max(max(vals), vmax)
        return (vmin, vmax)


class TargetProfiles(object):

    def __init__(self, owner, target,
                 treated_counts, untreated_counts,
                 treated_depths, untreated_depths,
                 treated_quality_depths, untreated_quality_depths):
        self.owner = owner
        self._target = target
        self.treated_counts = treated_counts
        self.untreated_counts = untreated_counts
        self.treated_depths = treated_depths
        self.untreated_depths = untreated_depths
        self.treated_quality_depths = treated_quality_depths
        self.untreated_quality_depths = untreated_quality_depths
        self.treated_muts = None
        self.untreated_muts = None
        self.treated_edge_muts = None
        self.untreated_edge_muts = None
        self.treated_removed_muts = None
        self.untreated_removed_muts = None
        self.treated_inserts = None
        self.treated_deletes = None
        self.untreated_inserts = None
        self.untreated_deletes = None

    @property
    def treated(self):
        return self.treated_counts

    @property
    def untreated(self):
        return self.untreated_counts

    @property
    def treated_depth(self):
        return self.treated_depths

    @property
    def untreated_depth(self):
        return self.untreated_depths

    @property
    def treated_quality_depth(self):
        return self.treated_quality_depths

    @property
    def untreated_quality_depth(self):
        return self.untreated_quality_depths

    @property
    def treated_mut(self):
        return self.treated_muts

    @property
    def untreated_mut(self):
        return self.untreated_muts

    @property
    def treated_insertions(self):
        return self.treated_inserts

    @property
    def untreated_insertion(self):
        return self.untreated_inserts

    @property
    def treated_deletions(self):
        return self.treated_deletes

    @property
    def untreated_deletions(self):
        return self.untreated_deletes

    @property
    def beta(self):
        return self.betas

    @property
    def theta(self):
        return self.thetas

    @property
    def rho(self):
        return self.rhos

    @property
    def r(self):
        return self.r_mut

    @staticmethod
    def _pooledStderr(c1, c2, n1, n2):
        if n1 * n2 == 0:
            return 0.0
        phat = float(c1 + c2) / float(n1 + n2)
        # TAI:  Is the last term correct / needed here?
        return math.sqrt(phat * (1.0 - phat) * ((1.0 / float(n1)) + (1.0 / float(n2))))

    def compute(self):
        treated_counts = self.treated_counts
        untreated_counts = self.untreated_counts
        treated_depths = self.treated_depths
        untreated_depths = self.untreated_depths
        n = len(treated_counts) - 1
        betas = [ 0 for x in range(n+1) ]
        thetas = [ 0 for x in range(n+1) ]
        z = [ 0 for x in range(n+1) ]
        running_c_sum = 0.0
        running_c_thresh_sum = 0.0

        # NOTE: there is an index discrepancy here between indices
        # used in the code, and the indices used in the Aviran paper
        # where these formulae are derived: the indices are
        # reversed. so, where in the paper the formula uses
        # \sum_{i=k}^{n+1}, in the code we use \sum_{i=0}^{k+1}, and
        # this is intentional.
        #
        # for reference, here is the comment from the original SPATS code:
        #  // TargetProfile tracks an RNA of length n. arrays have n+1 entries, 
        #  // with index 1 corresponding to the 5'-most base, and index n 
        #  // corresponding to the 3'-most base.  Index 0 stores information about 
        #  // unmodified RNAs, where RT has fallen off the 5' end of the 
        #  // strand.  This convention differs from the paper, where we refer to 
        #  // the 5'-most base as index n, and the 3'-most base as index 1.

        for k in range(n):
            X_k = float(treated_counts[k])
            Y_k = float(untreated_counts[k])
            try:
                Xbit = (X_k / float(treated_depths[k]))
                Ybit = (Y_k / float(untreated_depths[k]))
                betas[k] = (Xbit - Ybit) / (1 - Ybit)
                thetas[k] = math.log(1.0 - Ybit) - math.log(1.0 - Xbit)
                running_c_sum -= math.log(1.0 - betas[k])
                if not self.owner._run.allow_negative_values:
                    betas[k] = max(0.0, betas[k])
                    thetas[k] = max(0.0, thetas[k])
                running_c_thresh_sum -= math.log(1.0 - betas[k])
                if self.owner._run.compute_z_reactivity:
                    se = TargetProfiles._pooledStderr(treated_counts[k], untreated_counts[k], treated_depths[k], untreated_depths[k])
                    z[k] = (Xbit - Ybit) / se if se != 0 else (Xbit - Ybit)
                    if not self.owner._run.allow_negative_values:
                        z[k] = max(0.0, z[k])
            except:
                betas[k] = 0
                thetas[k] = 0
                z[k] = 0

        c_thresh = running_c_thresh_sum
        c_factor = 1.0 / c_thresh if c_thresh else 1.0
        for k in range(n+1):
            thetas[k] = max(c_factor * thetas[k], 0)
        self.betas = betas
        self.thetas = thetas
        self.rhos = [ n * th for th in thetas ]
        self.z = z
        self.c = running_c_sum
        self.c_thresh = c_thresh

        self.compute_mutated_profiles()

    def compute_mutated_profiles(self):
        if not self.treated_muts and not self.treated_inserts and not self.treated_deletes:
            return

        treated_depths = self.treated_depths
        untreated_depths = self.untreated_depths
        treated_counts = self.treated_counts
        untreated_counts = self.untreated_counts
        treated_muts = self.treated_muts
        untreated_muts = self.untreated_muts
        treated_removed_muts = self.treated_removed_muts
        untreated_removed_muts = self.untreated_removed_muts
        treated_inserts = self.treated_inserts
        untreated_inserts = self.untreated_inserts
        treated_deletes = self.treated_deletes
        untreated_deletes = self.untreated_deletes
        treated_quality_depths = self.treated_quality_depths
        untreated_quality_depths = self.untreated_quality_depths

        n = len(treated_counts) - 1
        mu = [ 0 for x in range(n+1) ]
        r_mut = [ 0 for x in range(n+1) ]
        z = [ 0 for x in range(n+1) ]
        running_c_sum = 0.0
        c_inf = False
        running_c_thresh_sum = 0.0
        c_thresh_inf = False

        # NOTE: there is an index discrepancy here between indices
        # used in the code, and the indices used in the derivation:
        # the indices are reversed. so, where formula uses
        # \sum_{i=j}^{n+1}, in the code we use \sum_{i=0}^{j+1}, and
        # this is intentional.

        for j in range(n):

            # mut_j^+ - Only one of { mut, insert, delete } is currently possible at a site per pair
            mut_j_t = 0
            if treated_muts:
                mut_j_t += float(treated_muts[j])
            if treated_inserts:
                mut_j_t += float(treated_inserts[j])
            if treated_deletes:
                mut_j_t += float(treated_deletes[j])

            # mut_j^- - Only one of { mut, insert, delete } is currently possible at a site per pair
            mut_j_u = 0
            if untreated_muts:
                mut_j_u += float(untreated_muts[j])
            if untreated_inserts:
                mut_j_u += float(untreated_inserts[j])
            if untreated_deletes:
                mut_j_u += float(untreated_deletes[j])

            try:
                # xref https://trello.com/c/10pysbq7/261-mutation-depth-with-quality-filtering-when-calculating-mus
                # if we removed a mut due to low quality, then we want to remove the corresponding stop
                # from the analysis (even though it should still be counted in the non-mut analysis).
                # so we use quality_depths here.
                Tbit = (mut_j_t / float(treated_quality_depths[j]))
                Ubit = (mut_j_u / float(untreated_quality_depths[j]))
                mu[j] = (Tbit - Ubit) / (1 - Ubit)

                if (self.owner._run.compute_z_reactivity  and
                    treated_quality_depths[j] + untreated_quality_depths[j] > 0  and
                    treated_depths[j] + untreated_depths[j] > 0):
                    se_z = TargetProfiles._pooledStderr(mut_j_t + mut_j_u, treated_counts[j] + untreated_counts[j], treated_quality_depths[j] + untreated_quality_depths[j], treated_depths[j] + untreated_depths[j])

                    Tboth = (mut_j_t + treated_counts[j]) / (0.5 * (treated_quality_depths[j] + treated_depths[j]))
                    Uboth = (mut_j_u + untreated_counts[j]) / (0.5 * (untreated_quality_depths[j] + untreated_depths[j]))
                    z[j] = (Tboth - Uboth) / se_z if se_z > 0 else (Tboth - Uboth)
                    if not self.owner._run.allow_negative_values:
                        z[k] = max(0.0, z[k])

                try:
                    running_c_sum -= math.log(1.0 - mu[j])  # xref Yu_Estimating_Reactivities pdf, p24
                except:
                    c_inf = True

                if not self.owner._run.allow_negative_values:
                    mu[j] = max(0.0, mu[j])

                try:
                    running_c_thresh_sum -= math.log(1.0 - mu[j])  # xref Yu_Estimating_Reactivities pdf, p24
                except:
                    c_thresh_inf = True

            except:
                #print("domain error: {} / {} / {} / {}".format(s_j_t, depth_t, s_j_u, depth_u))
                mu[j] = 0.0
                z[j] = 0.0

            r_mut[j] = self.betas[j] + mu[j]

        self.mu = mu
        self.r_mut = r_mut
        self.z = z
        if c_inf:
            self.c = float('inf')   # when c is infinite, pr of modification is 1
        else:
            self.c += running_c_sum
        if c_thresh_inf:
            self.c_thresh = float('inf')    # when c_thresh is infinite, pr of modification is 1
        else:
            self.c_thresh += running_c_thresh_sum


    def write(self, outfile):
        n = len(self.treated_counts)
        format_str = "{name}\t{rt}\t".format(name = self._target.name, rt = n - 1) + "{i}\t{nuc}\t{tm}\t{um}\t{b}\t{th}" + "\t{c:.5f}\n".format(c = self.c_thresh)
        for i in range(n):
            outfile.write(format_str.format(i = i,
                                            nuc = self._target.seq[i - 1] if i > 0 else '*',
                                            tm = self.treated_counts[i],
                                            um = self.untreated_counts[i],
                                            b = self.betas[i] if i > 0 else '-',
                                            th = self.thetas[i] if i > 0 else '-'))

    def data(self):
        return { "t" : self.treated_counts,
                 "u" : self.untreated_counts }
