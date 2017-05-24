
#ifndef __SPATS_PARSE_HPP_INCLUDED__
#define __SPATS_PARSE_HPP_INCLUDED__

typedef bool (*pair_handler)(Fragment * r1, Fragment * r2, const char * handle);

void
fastq_parse(const char * r1_path, const char * r2_path, pair_handler handler);

void
pairs_to_spin(const char * r1_path, const char * r2_path, const char * spin_path);


#endif  // __SPATS_PARSE_HPP_INCLUDED__
