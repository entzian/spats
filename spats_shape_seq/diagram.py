
import string

from target import _Target
from util import reverse_complement


indeterminate_translator = string.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ"," ! !!! !!!!!!!!!!!! !!!!!!")

def sp(n, bit = " "):
    return bit * n

class Diagram(object):

    def __init__(self, pair, run):
        self.target = pair.target or _Target('???', '?' * 100, 0)
        self.pair = pair
        self.run = run
        self.prefix_len = 16
        self.bars = []
        self.max_len = 0
        self.error_bars = None

    def match_index(self, part):
        if part.matched:
            return part.match_index
        elif part == self.pair.r1:
            margin = (self.target.n - part.original_len) >> 1
            return max(0, self.target.n - margin - part.original_len + 20)
        else:
            return max(0,  (self.target.n - (part.original_len) >> 1) - 20)

    def _make_prefix(self, label):
        bit = label[:min(self.prefix_len - 3, len(label))]
        return bit + sp(self.prefix_len - len(bit))

    def _make_target_lines(self):
        d = self._make_prefix("site")
        d = d[:-1]
        for i in range(0, self.target.n, 10):
            marker = str(i)
            if i > 0:
                marker = marker.replace('0','o')
            d += marker
            d += sp(10 - len(marker))
        self._add_line(d)

        d = self._make_prefix(self.target.name)
        d = d[:-1] + '^'
        seq = self.target.seq.lower()
        for part in [ self.pair.r1, self.pair.r2 ]:
            if part.match_len:
                start = self.match_index(part)
                end = start + part.match_len
                seq = seq[:start] + seq[start:end].upper() + seq[end:]
        d += seq
        self._add_line(d)

    def _add_indels(self, part, offset, seq):
        if part.indels:
            for index in sorted(part.indels.keys()):
                indel = part.indels[index]
                ind = index - offset
                if indel.insert_type:
                    seq = seq[:ind] + seq[ind + len(indel.seq):]
                else:
                    il = len(indel.seq)
                    seq = seq[:ind-il+1] + '*' * len(indel.seq) + seq[ind-il+1:]
                    part.match_errors.append(ind)
        return seq

    def _adj_front(self, part, d):
        is_R1 = (part == self.pair.r1)
        match_index = self.match_index(part)
        spaces = match_index
        if not is_R1:
            spaces -= part.ltrim
        elif part.rtrim:
            spaces -= (part.rtrim + 1)
        if spaces >= 0:
            d += sp(spaces)
        else:
            d = d[0:spaces]
        return d, match_index

    def _make_part(self, part):
        masklen = self.pair.mask.length() if self.pair.mask else 4
        is_R1 = (part == self.pair.r1)
        rlab = "<--R1--" if is_R1 else "--R2-->"
        _, match_index = self._adj_front(part, "")
        match_len = part.match_len if part.match_len else part.seq_len
        spacer = match_index + ((match_len - len(rlab)) >> 1)
        hdr = sp(spacer)
        hdr += rlab
        if is_R1:
            suffix = part.ltrim + 1
            hdr += sp(match_index + match_len - spacer - len(rlab) + suffix - masklen)
            if part.indels_delta > 0:
                hdr += sp(part.indels_delta)
            hdr += self.pair.mask.chars[::-1] if self.pair.mask else "?" * masklen
        self._add_line(self._make_prefix("") + hdr)

        d = self._make_prefix("rev(R1)" if is_R1 else "R2")
        d,_ = self._adj_front(part, d)
        if is_R1:
            if part.rtrim:
                d += (part.original_seq[-part.rtrim:][::-1] + ".")
            d += part.subsequence[::-1]
            if part.ltrim > masklen:
                d += part.original_seq[masklen:part.ltrim][::-1]
            if part.indels_delta < 0:
                d += sp(-part.indels_delta)
            d += ("." + part.original_seq[:min(masklen, part.ltrim)][::-1])
        else:
            d += part.original_seq[:part.ltrim]
            d += self._add_indels(part, match_index, part.subsequence)
            if part.rtrim:
                trimmed = part.original_seq[-part.rtrim:]
                linker_len = 0
                if self.run.cotrans and self.run._linker_trimmed:
                    linker_len = len(self.run.cotrans_linker)
                    d += trimmed[:linker_len]
                if len(trimmed) > linker_len:
                    d += ("." + trimmed[linker_len:linker_len + masklen])
                if len(trimmed) > linker_len + masklen:
                    d += ("." + trimmed[linker_len + masklen:])
        self._add_line(d)

        if part.matched:
            return [ self.prefix_len + part.match_index, self.prefix_len + part.match_index + part.match_len - 1 ]
        elif self.pair.failure == "indeterminate sequence failure":
            d = ""
            if is_R1:
                d += part.original_seq[-part.rtrim:][::-1].translate(indeterminate_translator) + "." 
                d += part.original_seq[::-1].translate(indeterminate_translator) + "."
                d += part.original_seq[:masklen][::-1].translate(indeterminate_translator)
            else:
                d += part.original_seq[:part.ltrim].translate(indeterminate_translator)
                d += part.subsequence.translate(indeterminate_translator)
                if part.rtrim:
                    trimmed = part.original_seq[-part.rtrim:].translate(indeterminate_translator)
                    if len(trimmed) < masklen:
                        d += ("." + trimmed)
                    else:
                        d += ("." + trimmed[:masklen] + "." + trimmed[masklen:])
            self._add_line(self._make_prefix("") + d)
            return []
        else:
            d = sp(match_index)
            d += sp(part.seq_len + part.indels_delta, "?")
            self._add_line(self._make_prefix("") + d)
            return []

    def _make_adapter_line(self, part, adapter, label):
        is_R1 = (part == self.pair.r1)
        dumblen = len(self.run.dumbbell) if self.pair.dumbbell else 0
        if is_R1:
            if part.right and part.rtrim > dumblen:
                alen = part.rtrim - dumblen
                d = self._make_prefix(label)
                d, match_index = self._adj_front(part, d)
                if alen > len(adapter):
                    d += sp(alen - len(adapter))
                    alen = len(adapter)
                if part.adapter_errors:
                    errors = sp(alen)
                    for e in part.adapter_errors:
                        if e < alen:
                            errors = errors[:e] + "!" + errors[e+1:]
                    errors = errors[::-1]
                    if errors[0] == " ":
                        errors = "|" + errors[1:]
                    if errors[-1] == " ":
                        errors = errors[:-1] + "|"
                    self._add_line(d + errors)
                d += adapter[:alen][::-1]
                self._add_line(d)
            if dumblen > 0:
                dumbbell_part = min(part.rtrim, dumblen)
                d = self._make_prefix('c(DUMBBELL)')
                d, _ = self._adj_front(part, d)
                d += sp(part.rtrim - dumbbell_part)
                d += reverse_complement(self.run.dumbbell[:dumbbell_part])[::-1]
                self._add_line(d)
        elif part.left and part.rtrim > dumblen:
            d = self._make_prefix(label)
            adjd, match_index = self._adj_front(part, d)
            if dumblen > 0:
                d += sp(self.pair.dumbbell)
                d += self.run.dumbbell
            else:
                d += sp(match_index)
            d += sp(part.match_len + 1)
            masklen = self.pair.mask.length()
            d += sp(masklen + 1)
            if self.run.cotrans:
                d += sp(len(self.run.cotrans_linker))
            d += (adapter[:part.rtrim - masklen] + "..")
            self._add_line(d)

    def _make_part_ins(self, part):
        label = "ins"
        d = label
        d += sp(self.prefix_len - len(d))
        ci = 0
        instodo = []
        for index in sorted(part.indels.keys()):
            indel = part.indels[index]
            if indel.insert_type:
                d += sp(index - ci)
                d += "V"
                ci = index + 1
                instodo.append((index, indel.seq))
        if not instodo:
            return
        lines_to_add = [ d ]
        while instodo:
            stilltodo = []
            d = label
            d += sp(self.prefix_len - len(d))
            ci = 0
            for ins in instodo:
                if ins[0] >= ci:
                    d += sp(ins[0] - ci)
                    d += ins[1]
                    ci = ins[0] + len(ins[1])
                else:
                    stilltodo.append(ins)
            lines_to_add.insert(0, d)
            instodo = stilltodo
        for line in lines_to_add:
            self._add_line(line)

    def _make_part_errors(self, part):
        match_index = self.match_index(part)
        d = sp(match_index)
        errors = sp(part.seq_len - part.indels_delta)
        error_bars = []
        _,q = part.apply_indels()
        for e in part.match_errors:
            bit = q[e] if q else "!"
            errors = errors[:e] + bit + errors[e+1:]
            error_bars.append(self.prefix_len + match_index + e)
        d += errors
        d += sp(self.target.n - len(d))
        if part == self.pair.r2 and part.adapter_errors:
            d += " "
            masklen = self.pair.mask.length()
            d += sp(masklen + 1)
            errors = sp(part.rtrim - masklen)
            for e in part.adapter_errors:
                errors = errors[:e] + "!" + errors[e+1:]
            if errors[0] == " ":
                errors = "|" + errors[1:]
            if errors[-1] == " ":
                errors = errors[:-1] + "|"
            d += errors
        self._add_line(self._make_prefix("-mutQ30") + d)
        if error_bars:
            self.bars.append(error_bars)
            return error_bars
        return None

    def _make_part_quality(self, part):
        if not part.quality:
            return
        d = sp(self.match_index(part))
        _,q = part.apply_indels()
        q = q[part.match_start:(part.match_start or 0) + part.match_len]
        self._add_line(self._make_prefix("-allQ30") + d + (q or ""))

    def _make_r1_rev(self):
        r1 = self.pair.r1
        d = "revcomp(R1)"
        d += sp(r1.match_index + self.prefix_len - len(d))
        d += self._add_indels(r1, r1.match_index, r1.reverse_complement)
        self._add_line(d)

    def _make_linker(self):
        d = "LINKER"
        d += sp(self.pair.linker + self.prefix_len - len(d))
        d += self.run.cotrans_linker
        self._add_line(d)

    def _make_result(self, part):
        match_index = self.match_index(part)
        d = sp(match_index)
        l = "l={}".format(match_index)
        r = "r={}".format(match_index + part.match_len)
        masklen = self.pair.mask.length()
        leftover = part.match_len - len(l) - len(r) - masklen
        if leftover < 0:
            l = l[2:]
            r = r[2:]
            leftover = max(0, part.match_len - len(l) - len(r) - masklen)
        halfish = (leftover >> 1)
        bit = "^{}{}, {}{}^".format("-"*halfish,l,r,"-"*(leftover - halfish))
        d += bit
        self._add_line(sp(self.prefix_len) + d)

    def _add_marker(self, label, index):
        # note: the delta for 'Mut' and 'End' is to make diagram and off-by-one conventions align better
        # xref 'conventions' below
        self._add_line(sp(self.prefix_len + index) + '^--- {} = {}'.format(label, index + (1 if ('Mut' in label or 'End' in label) else 0)))

    def _add_line(self, line):
        if len(line) < self.max_len:
            line += sp(self.max_len - len(line))
        self.max_len = max(self.max_len, len(line))
        for bar_list in self.bars:
            for bar in bar_list:
                if bar <= 0:
                    print('ignoring bad bar: {}'.format(bar))
                    continue
                if len(line) > bar:
                    if line[bar] == ' ':
                        line = line[:bar] + '|' + line[(bar+1):]
                    elif line[bar] == '-':
                        line = line[:bar] + '+' + line[(bar+1):]
        if line.startswith("@") or line.startswith("\\"):
            pass
        elif line.startswith(" "):
            line = "|" + line
        else:
            line = "+" + line
        self.lines.append(line)

    def _make_summary(self):
        result = "\===>  "
        if self.pair.has_site:
            result += "++SITE {}:{}".format(self.pair.mask.chars, self.pair.site)
        else:
            result += "FAIL: {}".format(self.pair.failure)
        self.lines.append(result)

    def _snip_lines(self, start, end):
        for i in range(len(self.lines)):
            line = self.lines[i]
            snip = line[start:end]
            replace = "  " if snip == sp(end-start) else ".."
            self.lines[i] = line[:start] + replace + line[end:]

    def make(self):
        self.lines = [ ]

        # handling left-of-target matches
        masklen = self.pair.mask.length()
        self.prefix_len += max(self.pair.r1.rtrim - (self.pair.r1.match_index or 0) + 1,
                               self.pair.r2.ltrim, max(-self.match_index(self.pair.r2), 0))

        self._add_line("@" + self.pair.identifier)
        
        r1_bars = self._make_part(self.pair.r1)
        self.bars.append(r1_bars)
        if self.pair.r1.trimmed:
            self._make_adapter_line(self.pair.r1, self.run.adapter_b, "adapter_b")

        if self.pair.mask and self.pair.r1.matched:
            self._add_line("")
            if self.pair.r1.indels:
                self._make_part_ins(self.pair.r1)
            self._make_r1_rev()

        if self.pair.r1.match_errors or self.pair.r1.adapter_errors:
            r1_errors = self._make_part_errors(self.pair.r1)
        else:
            r1_errors = None
        if self.show_quality:
            self._make_part_quality(self.pair.r1)

        if self.pair.linker != None:
            self._make_linker()

        self._add_line("")

        if self.pair.r2.indels:
            self._make_part_ins(self.pair.r2)
        r2_bars = self._make_part(self.pair.r2)
        self.bars.append(r2_bars)
        if self.pair.r2.match_errors or self.pair.r2.adapter_errors:
            r2_errors = self._make_part_errors(self.pair.r2)
        else:
            r2_errors = None
        if self.show_quality:
            self._make_part_quality(self.pair.r2)
        if self.pair.r2.trimmed:
            label = "DB+RC(adp_t)" if self.pair.dumbbell else "RC(adapter_t)"
            self._make_adapter_line(self.pair.r2, reverse_complement(self.run.adapter_t), label)

        self._add_line("")

        self._make_target_lines()
        if r1_errors:
            self.bars.remove(r1_errors)
        if r2_errors:
            self.bars.remove(r2_errors)

        features = {}
        if self.pair.site != None:
            features['Site'] = self.pair.site
        if self.pair.end != None:
            # note: decrement to make off-by-one conventions align better
            # xref 'conventions' above
            features['End'] = self.pair.end - 1
        if self.pair.mutations:
            idx = 1
            for mut in self.pair.mutations:
                if self.pair.edge_mut and mut + 1 == self.pair.site:
                    # note: decrement to make off-by-one conventions align better
                    # xref 'conventions' above
                    features['EdgeMut{} ({})'.format(idx, self.pair.edge_mut)] = mut - 1
                else:
                    # note: decrement to make off-by-one conventions align better
                    # xref 'conventions' above
                    features['Mut{}'.format(idx)] = mut - 1
                idx += 1
        for v in features.values():
            self.bars.append([v + self.prefix_len])

        if self.pair.r2.matched:
            self._make_result(self.pair.r2)
        self.bars.remove(r2_bars)
        if self.pair.r1.matched:
            self._make_result(self.pair.r1)
        else:
            self._add_line("")
        self.bars.remove(r1_bars)

        for key, value in features.items():
            self._add_marker(key, value)
            self.bars.remove([value + self.prefix_len])

        if self.pair.matched and self.pair.left > 100:
            self._snip_lines(self.prefix_len + 15, self.prefix_len + 85)

        self._add_line("")
        self._make_summary()

        return "\n".join(self.lines)

def diagram(pair, run, show_quality = False):
    d = Diagram(pair, run)
    d.show_quality = show_quality
    return d.make()
