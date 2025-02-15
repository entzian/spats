
import datetime
import os
import struct
from sys import version_info

import spats_shape_seq
from spats_shape_seq.mask import match_mask_optimized, Mask


# not currently used in spats, but potentially useful for tools
class FastqRecord(object):

    def __init__(self):
        self.recordNumber = 0
        self.reset()

    def reset(self):
        self.identifier = None
        self.tag = None
        self.sequence = None
        self.identifier2 = None
        self.quality = None

    def read(self, infile):
        first = infile.readline()
        if not first:
            self.reset()
            return False
        self.parse([ first, infile.readline(), infile.readline(), infile.readline() ])
        return True

    def parse(self, lines):
        self.identifier, self.tag = lines[0].lstrip('@').rstrip('\r\n').split(' ')
        self.sequence = lines[1].rstrip('\r\n')
        self.identifier2 = lines[2].rstrip('\r\n')
        self.quality = lines[3].rstrip('\r\n')

    def write(self, outfile, skiplen = 0):
        outfile.write("@{} {}\n".format(self.identifier, self.tag))
        for line in [ self.sequence[skiplen:], self.identifier2, self.quality[skiplen:] ]:
            outfile.write(line)
            outfile.write('\n')

    def reverse_complement(self):
        self.sequence = reverse_complement(self.sequence)
        self.quality = self.quality[::-1]


class FastFastqParser(object):

    def __init__(self, r1_path, r2_path, parse_quality = False):
        self.r1_path = r1_path
        self.r2_path = r2_path
        self.parse_quality = parse_quality

    def pair_length(self):
        with open(self.r1_path, 'rt') as r1_in:
            with open(self.r2_path, 'rt') as r2_in:
                r1_in.readline()
                r1_first = r1_in.readline().strip('\r\n')
                r2_in.readline()
                r2_first = r2_in.readline().strip('\r\n')
                pair_length = len(r1_first)
                if pair_length != len(r2_first):
                    print("Warning: pair length mismatch in R1 vs R2: {} / {}".format(pair_length, len(r2_first)))
                    return -1
                return pair_length

    def appx_number_of_pairs(self):
        with open(self.r1_path, 'rt') as r1_in:
            # the +1 is since first records tend to be short, and we'd rather underestimate than overestimate
            frag_len = 1 + len(r1_in.readline()) + len(r1_in.readline()) + len(r1_in.readline()) + len(r1_in.readline())
        return int(float(os.path.getsize(self.r1_path)) / float(frag_len))

    def __enter__(self):
        self.r1_in = open(self.r1_path, 'rt')
        self.r2_in = open(self.r2_path, 'rt')
        self.r1_iter = iter(self.r1_in)
        self.r2_iter = iter(self.r2_in)
        return self

    def __exit__(self, type, value, traceback):
        self.r1_in.close()
        self.r2_in.close()
        self.r1_in = None
        self.r2_in = None
        self.r1_iter = None
        self.r2_iter = None

    def iterator(self, batch_size):
        while True:
            batch = self.iterator_read(batch_size)
            if batch:
                yield batch
            else:
                return

    # kept separate from other read fns for speed
    def iterator_read(self, batch_size):
        pairs = []
        r1_iter = self.r1_iter
        r2_iter = self.r2_iter
        count = 0
        include_quality = self.parse_quality
        try:
            while count < batch_size:
                R1_id = next(r1_iter) #.split(' ')[0]
                R1_seq = next(r1_iter).rstrip('\n\r')
                next(r1_iter)
                R1_q = next(r1_iter)
                R2_id = next(r2_iter) #.split(' ')[0]
                R2_seq = next(r2_iter).rstrip('\n\r')
                next(r2_iter)
                R2_q = next(r2_iter)
                if 0 == count:
                    # good enough to just spot-check this, and improve parsing speed by skipping most of the time
                    R1_id = R1_id.split(' ')[0]
                    R2_id = R2_id.split(' ')[0]
                    if R1_id != R2_id:
                        raise Exception("Malformed input files, id mismatch: {} != {}".format(R1_id, R2_id))
                if include_quality:
                    pairs.append((1, R1_seq, R2_seq, R1_id.split(' ')[0], R1_q.rstrip('\n\r'), R2_q.rstrip('\n\r')))
                else:
                    pairs.append((1, R1_seq, R2_seq, str(count)))
                count += 1
        except StopIteration:
            pass
        return pairs

    # returns a list of (id, r1, r2), of length <= max_num_pairs, len<max_num_pairs iff eof
    def read(self, max_num_pairs):
        pairs = []
        count = 0
        r1_iter = self.r1_iter
        r2_iter = self.r2_iter
        try:
            while count < max_num_pairs:
                R1_id = next(r1_iter).split(' ')[0]
                R1_seq = next(r1_iter).rstrip('\n\r')
                next(r1_iter)
                next(r1_iter)
                R2_id = next(r2_iter).split(' ')[0]
                R2_seq = next(r2_iter).rstrip('\n\r')
                next(r2_iter)
                next(r2_iter)
                if R1_id != R2_id:
                    raise Exception("Malformed input files, id mismatch: {} != {}".format(R1_id, R2_id))
                pairs.append((R1_id.lstrip('@'), R1_seq, R2_seq))
                count += 1
        except StopIteration:
            pass
        return pairs, count

    # returns a list of (numeric_id, r1, r2, original_id), of length <= max_num_pairs, len<max_num_pairs iff eof
    # separate function in order to keep read() optimized for standard case
    def read_nomask(self, max_num_pairs):
        pairs = []
        count = 0
        r1_iter = self.r1_iter
        r2_iter = self.r2_iter
        try:
            while count < max_num_pairs:
                R1_numeric_id = int(next(r1_iter).strip('@\n\r'))
                R1_seq = next(r1_iter).rstrip('\n\r')
                R1_original_id = next(r1_iter).strip('+\n\r')
                next(r1_iter)
                R2_numeric_id = int(next(r2_iter).strip('@\n\r'))
                R2_seq = next(r2_iter).rstrip('\n\r')
                R2_original_id = next(r2_iter).strip('+\n\r')
                next(r2_iter)
                if R1_numeric_id != R2_numeric_id or R1_original_id != R2_original_id:
                    raise Exception("Malformed NOMASK files, id mismatch: ({},{}) != ({},{})".format(R1_numeric_id, R1_original_id, R2_numeric_id, R2_original_id))
                pairs.append((R1_numeric_id, R1_seq, R2_seq, R1_original_id))
                count += 1
        except StopIteration:
            pass
        return pairs, count

class FastqWriter(object):

    def __init__(self, r1_path, r2_path):
        self.r1_path = r1_path
        self.r2_path = r2_path
        self.r1_out = open(self.r1_path, 'w')
        self.r2_out = open(self.r2_path, 'w')

    def _write_seq(self, out, pair, seq, trim_handle):
        out.write('{}{}\n{}\n+\n{}\n'.format('' if pair.identifier.startswith('@') else '@', pair.identifier,
                                             seq.original_seq[pair.mask.length():] if trim_handle else seq.original_seq,
                                             seq.quality[pair.mask.length():] if trim_handle else seq.quality))

    def write(self, pair):
        self._write_seq(self.r1_out, pair, pair.r1, trim_handle = True)
        self._write_seq(self.r2_out, pair, pair.r2, trim_handle = False)

    def close(self):
        if self.r1_out:
            self.r1_out.close()
            self.r2_out.close()
            self.r1_out = None
            self.r2_out = None


class _MaskMatcher:
    def __init__(self, masks):
        if len(masks) == 2  and  'RRRY' in masks  and  'YYYR' in masks:
            self.match_mask = match_mask_optimized
        else:
            self.match_mask = self._match_mask
            self.masks = []
            for mask in masks:
                self.masks.append(Mask(mask))

    def _match_mask(self, seq):
        for mask in self.masks:
            if mask.matches(seq):
                return mask.chars
        return None

def fastq_handle_filter(r1_path, r2_path, masks = [ 'RRRY', 'YYYR' ], strip_mask = False, outpath = '.', counters = None):
    # creates 4 files, one for each mask for r1_path and r2_path.
    # output filenames are the originals with the mask name prefixed (nukes them if they exist already)
    # returns the list of output files
    result = None if len(masks) == 0 else []
    r1of = {}
    r2of = {}
    def _channelFilename(combined_path, handle, outpath):
        comboname = os.path.basename(combined_path)
        if comboname.endswith(".tmp"):
            comboname = comboname[:-4]
        return os.path.abspath(os.path.join(outpath, handle + '-' + comboname))
    for mask in masks:
        if len(mask) == 0:
            raise Exception("handle_filter cannot be used with a handle/mask length of 0.")
        r1fpath = _channelFilename(r1_path, mask, outpath)
        r1of[mask] = open(r1fpath, 'w+')
        result.append(r1fpath)
        r2fpath = _channelFilename(r2_path, mask, outpath)
        r2of[mask] = open(r2fpath, 'w+')
        result.append(r2fpath)
    mm = _MaskMatcher(masks)
    try:
        fqr1 = FastqRecord()
        fqr2 = FastqRecord()
        with open(r1_path, 'r') as r1if, open(r2_path, 'r') as r2if:
            while fqr1.read(r1if) and fqr2.read(r2if):
                mask = mm.match_mask(fqr1.sequence)
                if mask:
                    striplen = len(mask) if strip_mask else 0
                    fqr1.write(r1of[mask], striplen)
                    fqr2.write(r2of[mask])
                    if counters:
                        counters.increment_key(mask)
                elif counters:
                    counters.increment_key('no_mask')
    finally:
        for mask in masks:
            r1of[mask].close()
            r2of[mask].close()
    return result


def fasta_parse(target_path):
    pairs = []
    with open(target_path, 'rt') as infile:
        def nextline():
            while True:
                l = infile.readline()
                if len(l) == 0:
                    return l
                l = l.strip('>\r\n')
                if 0 < len(l):
                    return l
        while True:
            name = nextline()
            if not name:
                break
            seq = nextline()
            if name and seq:
                pairs.append((name.strip(), seq))
    return pairs


class SamRecord(object):

    def parse(self, line):
        bits = line.split("\t")
        if len(bits) < 6:
            self.identifier = None
            return
        self.identifier = bits[0]
        self.flags = int(bits[1])
        self.target_name = bits[2]
        self.left = int(bits[3]) - 1 # TODO: subtract 1 is required, explain
        self.quality = int(bits[4])
        if self.target_name == '*':
            self.left = -1
            self.target_name = None
            self.right = -1
            return
        lengthPart = bits[5][:-1]
        self.length = int(lengthPart if len(lengthPart) > 0 else 0)
        if self.length > 0 and "M" != bits[5][-1]:
            raise Exception("Expected M on SAM length field, got: {}".format(bits[5]))
        # rest of bits are not used afaict
        self.right = self.left + self.length

    def dump(self):
        return '\t'.join([self.identifier, str(self.flags), self.target_name or '*', str(self.left + 1), self.quality,
                          '{}M'.format(self.right - self.left) if self.target_name else '0', '=' if self.target_name else '*',
                          # TODO: last three vals
                          '?', '?', 'SEQ'])


class SamWriter(object):

    def __init__(self, path, targets, write_failures = True):
        self.write_failures = write_failures
        self.path = path
        self.sam_out = open(self.path, 'w')
        self._write_header(targets)

    def _write_header(self, targets):
        self.sam_out.write('@HD	VN:1.0	SO:unsorted\n')
        for t in targets:
            self.sam_out.write('@SQ	SN:{}	LN:{}\n'.format(t.name, t.n))
        self.sam_out.write('@PG	ID:spats_shape_seq	VN:{}	CL:"spats_tool run"\n'.format(spats_shape_seq._VERSION))

    def write(self, pair):
        qname = pair.identifier
        r2_seq = pair.r2.subsequence
        r1_seq = pair.r1.reverse_complement
        r2_q = pair.r2.subquality
        r1_q = pair.r1.reverse_quality
        if pair.failure:
            r2_flag = 141
            r1_flag = 77
            rname = r1_cigar = r2_cigar = rnext = '*'
            r2_pos = r1_pos = mapq = r1_pnext = r2_pnext = r2_tlen = r1_tlen = 0
            alignment = 'XM:i:0'
            if self.write_failures:
                alignment += ' f:Z:{}'.format(pair.failure)
            r1_align = r2_align = alignment
        else:
            r2_flag = 163
            r1_flag = 83
            rname = pair.target.name
            r2_pos = pair.r2.left + 1
            r1_pos = pair.r1.left + 1
            mapq = 255
            r2_cigar = '{}M'.format(len(r2_seq))
            r1_cigar = '{}M'.format(len(r1_seq))
            rnext = '='
            r2_pnext = pair.r1.left + 1
            r1_pnext = pair.r2.left + 1
            r2_tlen = pair.length
            r1_tlen = 0 - pair.length
            r2_align = 'XA:i:0	MD:Z:{}	NM:i:0'.format(len(r2_seq))
            r1_align = 'XA:i:0	MD:Z:{}	NM:i:0'.format(len(r1_seq))
        for row in ( [ qname, r2_flag, rname, r2_pos, mapq, r2_cigar, rnext, r2_pnext, r2_tlen, r2_seq, r2_q, r2_align ],
                     [ qname, r1_flag, rname, r1_pos, mapq, r1_cigar, rnext, r1_pnext, r1_tlen, r1_seq, r1_q, r1_align ] ):
            self.sam_out.write('\t'.join([ str(x) for x in row ]))
            self.sam_out.write('\n')

    def close(self):
        if self.sam_out:
            self.sam_out.close()
            self.sam_out = None


class SamParser(object):

    def __init__(self, path, target_map):
        self.sam_path = path
        self.target_map = target_map

    def __enter__(self):
        self.sam_in = open(self.sam_path, 'rt')
        self.sam_iter = iter(self.sam_in)
        return self

    def __exit__(self, type, value, traceback):
        self.sam_in.close()
        self.sam_in = None
        self.sam_iter = None

    # returns a list of (target, site, end, mask, numeric_id) -- the 'mask' is convenience to not have to recreate lists when inserting in DB
    def read(self, max_num_pairs, mask, cotrans = False, single_target = None):
        pairs = []
        count = 0
        sam_iter = self.sam_iter
        r1 = SamRecord()
        r2 = SamRecord()

        def nextline():
            while True:
                l = next(sam_iter)
                if not l.startswith('@'):
                    return l

        try:
            while count < max_num_pairs:
                r1.parse(nextline())
                r2.parse(nextline())
                if not r1.identifier or r1.identifier != r2.identifier:
                    raise Exception("Parse error?") # might just want continue?
                if not r1.target_name or single_target and single_target != r1.target_name:
                    continue
                left = min(r1.left, r2.left)
                right = max(r1.right, r2.right)
                if cotrans:
                    target_length = 20 + int(r1.target_name[r1.target_name.rfind('_')+1:-2])
                    if left >= 0 and left <= target_length and right == target_length:
                        pairs.append((left, right - 20, mask, r1.identifier))
                else:
                    target_length = len(self.target_map[r1.target_name])
                    if left >= 0 and left <= target_length and right == target_length:
                        pairs.append((r1.target_name, left, right, mask, r1.identifier))
                count += 1
        except StopIteration:
            pass
        return pairs, count


# return list of (target, rt_start, site, nuc, treated_count, untreated_count, beta, theta, c)
# all strings
def reactivities_parse(path):
    sites = []
    with open(path, 'rt') as infile:
        infile.readline() # ignore header line
        while True:
            line = infile.readline()
            if not line:
                break
            sites.append(line.split('\t'))
    return sites



##################################
# abif parsing modified from http://github.com/bow/abifpy
##################################


# dictionary for unpacking tag values
_BYTEFMT = {
            1: 'b',     # byte
            2: 's',     # char
            3: 'H',     # word
            4: 'h',     # short
            5: 'i',     # long
            6: '2i',    # rational, legacy unsupported
            7: 'f',     # float
            8: 'd',     # double
            10: 'h2B',  # date
            11: '4B',   # time
            12: '2i2b', # thumb
            13: 'B',    # bool
            14: '2h',   # point, legacy unsupported
            15: '4h',   # rect, legacy unsupported
            16: '2i',   # vPoint, legacy unsupported
            17: '4i',   # vRect, legacy unsupported
            18: 's',    # pString
            19: 's',    # cString
            20: '2i',   # Tag, legacy unsupported
           }

# header structure
_HEADFMT = '>4sH4sI2H3I'

# directory data structure
_DIRFMT = '>4sI2H4I'

def py3_get_string(byte):
    if version_info[0] < 3:
        return byte
    else:
        return byte.decode()

def py3_get_byte(string):
    if version_info[0] < 3:
        return string
    else:
        return string.encode()

class _Trace(object):

    def __init__(self, in_file, fields):
        self._fields = fields
        self._handle = open(in_file, 'rt')
        try:
            self._handle.seek(0)
            if not self._handle.read(4) == py3_get_byte('ABIF'):
                raise IOError('Input is not a valid trace file')
        except IOError:
            self._handle = None
            raise
        else:
            # header data structure:
            # file type, file, version, tag name, tag number, element type code,
            # element size, number of elements, data size, data offset, handle,
            # file type, file version
            self.data = {}
            self.tags = {}
            self._handle.seek(0)
            header = struct.unpack(_HEADFMT, 
                                   self._handle.read(struct.calcsize(_HEADFMT)))
            self.version = header[1]

            for entry in self._parse_header(header):
                key = entry.tag_name + str(entry.tag_num)
                #print "KEY: " + str(key) + " -- " + str(entry.data_size)
                self.tags[key] = entry
                if key in self._fields:
                    self.data[key] = self.get_data(key)

    def _parse_header(self, header):
        # header structure:
        # file signature, file version, tag name, tag number, 
        # element type code, element size, number of elements
        # data size, data offset, handle
        head_elem_size = header[5]
        head_elem_num = header[6]
        head_offset = header[8]
        index = 0
        while index < head_elem_num:
            start = head_offset + index * head_elem_size
            # added directory offset to tuple
            # to handle directories with data size <= 4 bytes
            self._handle.seek(start)
            dir_entry =  struct.unpack(_DIRFMT, self._handle.read(struct.calcsize(_DIRFMT))) + (start,)
            index += 1
            yield _TraceDir(dir_entry, self._handle)

    def get_data(self, key):
        return self.tags[key].tag_data


class _TraceDir(object):
    def __init__(self, tag_entry, handle):
        self.tag_name = py3_get_string(tag_entry[0])
        self.tag_num = tag_entry[1]
        self.elem_code = tag_entry[2]
        self.elem_size = tag_entry[3]
        self.elem_num = tag_entry[4]
        self.data_size = tag_entry[5]
        self.data_offset = tag_entry[6]
        self.data_handle = tag_entry[7]
        self.tag_offset = tag_entry[8]

        # if data size is <= 4 bytes, data is stored inside the directory
        # so offset needs to be changed
        if self.data_size <= 4:
            self.data_offset = self.tag_offset + 20

        self.tag_data = self._unpack(handle)

    def _unpack(self, handle):

        if self.elem_code in _BYTEFMT:
            # because ">1s" unpacks differently from ">s"
            num = '' if self.elem_num == 1 else str(self.elem_num)
            fmt = "{0}{1}{2}".format('>', num, _BYTEFMT[self.elem_code])
            start = self.data_offset

            handle.seek(start)
            data = struct.unpack(fmt, handle.read(struct.calcsize(fmt)))

            if self.elem_code not in [10, 11] and len(data) == 1:
                data = data[0]

            if self.elem_code == 2:
                return py3_get_string(data)
            elif self.elem_code == 10:
                return datetime.date(*data)
            elif self.elem_code == 11:
                return datetime.time(*data)
            elif self.elem_code == 13:
                return bool(data)
            elif self.elem_code == 18:
                return py3_get_string(data[1:])
            elif self.elem_code == 19:
                return py3_get_string(data[:-1])
            else:
                return data
        else:
            return None

# return list of data values associated with each passed-in field
def abif_parse(filename, fields = [ 'DATA1', 'DATA2', 'DATA3', 'DATA4', 'DATA105' ]):
    t = _Trace(filename, fields)
    return [ t.data[x] for x in fields ]
