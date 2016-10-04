import argparse, os, subprocess, fnmatch, Gnuplot, Gnuplot.funcutils

#Models a transcript using data from the Alamut genes file 
class Gnuplotter():
    def __init__(self, interval_exons, interval_extended, plottable_coverage, exome_identifier, gene, length_of_extended_transcript):
        self.interval_exons = interval_exons
	self.interval_extended = interval_extended
	self.plottable_coverage = str(plottable_coverage)
	self.exome_identifier = exome_identifier
	self.gene = gene
	self.length_of_extended_transcript = length_of_extended_transcript

    def coverage_plot(self):
        #plot 'test.dat' u 2:3:1 w labels point offset character 0,character 1 tc rgb "blue"
	g = Gnuplot.Gnuplot(debug=1)
	g('set terminal svg size 5000, 500')
        file_name = str(self.gene) + '.svg'
	output = 'set output ' + '"' + str(self.exome_identifier) + '_' + str(self.gene) + '.svg' + '"'
	g(output)
	g("set datafile separator ','")
	g('set style line 1 lt 1 lw 2 lc 3')
	g("set style line 2 lt 2 lw 10 lc rgb 'navy'")
	g("set style line 3 lt 3 lw 1 lc rgb 'black'")
	g("set object rect from 0,0 to 8878,0.2")
	g("set style rect back fc rgb 'beige' fs solid 1.0 noborder")
	g("min(a,b) = (a < b) ? a : b")
	g("f(x) = min(1.0, (log(x + 10.0) - log(10.0)) / 4.0)")
	g("set ytics ('0' f(0), '5' f(5), '10' f(10), '20' f(20), '40' f(40), '100' f(100), '200' f(200), '400' f(400), '800' f(800), '1600' f(1600))")
	string_alternative = str(self.plottable_coverage)
	g('plot ' + '"' + string_alternative + '"' + ' using 1:(f($2)) with lines ls 3, ' + '-0.1 title ' + '"' + self.gene + '"' + ' with lines ls 3, ' + '0.2 title ' + '"' + '20x' + '"' + ' with lines ls 3' + ', "' + self.interval_exons + '"' + ' with lines ls 2' + ', "' + self.interval_extended + '"' + ' with lines ls 1')
         
class Transcript():

    def __init__(self, alamut_line):
        self.alamut_line = alamut_line
	self.gene_symbol = self.alamut_line[1]
        print 'gene_symbol = ' + self.gene_symbol
        self.transcript_id = self.alamut_line[7]
        print 'trans_id = ' + self.transcript_id
        self.cds_start = self.alamut_line[10]
        self.cds_end = self.alamut_line[11]
        self.cds_length = int(self.cds_end) - int(self.cds_start) + 1
        self.chromosome = self.alamut_line[3]
	self.strand = self.alamut_line[6]
        self.gene_start = self.alamut_line[4]
        self.gene_stop = self.alamut_line[5]
        self.exons = {self.alamut_line[12] : [self.alamut_line[15], self.alamut_line[16]]}

#split this into three funcitons
    def generate_transcript_range(self, input_file, transcript_instance):
	extended = []
	exons = []
	range_array = []
        with open(input_file, 'r') as input:
            for line in input:
                split_line = line.split(',')
                ranger = (int(split_line[4]) - int(split_line[3])) + 1
                extended.append(ranger)
		exon = (int(split_line[2]) - int(split_line[1])) + 1
		exons.append(exon)
            	for i in range(int(split_line[3]), int(split_line[4]) + 1, 1):
                    i = [str(transcript_instance.chromosome), str(i), split_line[0]]
                    range_array.append(i)
	extended_intervals = input_file + '.extended'
	with open(extended_intervals, 'w') as extended_interval_file:
	    count1 = 0
	    for item in extended:
		extension = 0
		exon_length = item - 100
		end_of_exon = item - 50
		for i in range(int(item)):
		    count1 += 1
		    extension += 1
		    if extension <= 50:
		        extended_interval_file.write(str(count1)+',-0.05\n')
		    elif extension > 50 and extension <= end_of_exon:
			extended_interval_file.write('\n')
		    elif extension > end_of_exon:
			extended_interval_file.write(str(count1)+',-0.05\n')
	exon_file_name = input_file + '.exons'
	with open(exon_file_name, 'w') as exon_interval_file:
	    count2 = 0
	    for item in extended:
		extension2 = 0
		exon_lengeth = item - 100
		end_of_exon = item - 50
		for i in range(int(item)):
		    count2 += 1
		    extension2 += 1
		    if extension2 <= 50:
		        exon_interval_file.write('\n')
		    elif extension2 > 50 and extension2 <= end_of_exon:
			exon_interval_file.write(str(count2)+',-0.05\n')
		    elif extension2 > end_of_exon:
		        exon_interval_file.write('\n')
        return range_array


class Coverage_parser(Transcript):

    transcript_instances = []
    exome_coverage_files = ''

    def __init__(self, sample_name_file, gene_name_file, alamut_file):
        self.sample_list = self.list_from_file(sample_name_file)
        self.gene_list = self.list_from_file(gene_name_file)
	self.alamut_file = alamut_file

    def line_strip_split(self, line):
        line = line.strip('\n')
        split_line = line.split()
        return split_line

    def list_from_file(self, input_file):
        new_list = []
        with open(input_file, 'r') as inputfile:
            for line in inputfile:
                line = line.strip()
                new_list.append(line)
        return new_list

    def exome_coverage_finder_bash(self):
	exome_coverage_files = []
        print 'finding coverage files for : '
        print (self.sample_list)
	sample_iteration = 0
   	for exome_sample in self.sample_list:
	    exome_sample = exome_sample.strip('\n')
	    coverage_dict = {}
	    command = ["bash", "all_exome_coverage_files", exome_sample]
	    process = subprocess.Popen(command, stdout=subprocess.PIPE)
	    cov_file_path = process.communicate()[0].strip('\n')
	    #communicate output
	    coverage_dict[exome_sample] = cov_file_path
            exome_coverage_files.append(coverage_dict)
        self.exome_coverage_files = exome_coverage_files
        return exome_coverage_files

    def find_gene_intervals(self):
        lines_parsed = 0
        with open(self.alamut_file, 'r') as alamut_file:
            for line in alamut_file:
                for gene in self.gene_list:
                    #if its the first line
                    if gene in line and len(self.transcript_instances) == 0:
                        line = line.split()
			if gene == line[1] or gene == line[7]:
                            initial_transcript_instance = Transcript(line)  
			    self.transcript_instances.append(initial_transcript_instance)
		    elif gene in line and len(self.transcript_instances) > 0:
		        line = line.split()
			#if gene is symbol or transcript
			if gene == line[1] or gene == line[7]:
			    if self.transcript_instances[-1].transcript_id == line[7] and line [12] not in self.transcript_instances[-1].exons:
			        self.transcript_instances[-1].exons[line[12]] = [line[15], line [16]]
			    if self.transcript_instances[-1].transcript_id != line[7]:
			        additional_transcript_instance = Transcript(line)
			        self.transcript_instances.append(additional_transcript_instance)

    #need to account for it they are equal
    def longest_transcript(self):
        longest_transcripts = []
	current_longest = []
        #iterate through the gene list provided
        print 'identifying longest transcripts'
        for gene in self.gene_list:
            this_gene = []
            current_longest = []
            #iterate through the all transcript list of objects
            for item in self.transcript_instances:
                if gene == item.__dict__['gene_symbol'] or gene == item.__dict__['transcript_id']:
                    if len(current_longest) == 0:
                        this_gene.append(item)
                        current_longest.append(item)
                    elif len(current_longest) == 1:
                        this_gene.append(item)
            for item in this_gene:
	        current = int(current_longest[-1].__dict__['cds_length'])
                challenger = int(item.__dict__['cds_length'])
                if challenger > current:
                    current_longest[-1] = item
            longest_transcripts.append(current_longest[-1])
        print 'the longest transcripts are:'
        for item in longest_transcripts:
            print str(item.__dict__['gene_symbol']) + ' ' + str(item.__dict__['transcript_id']) + '\n'
        return longest_transcripts

    def exon_interval_file_creator(self, transcript_instance):
        print 'creating exon interval files : ' + transcript_instance.__dict__['transcript_id']
	if transcript_instance.__dict__['strand'] == '-1':
	    output_name = transcript_instance.__dict__['transcript_id'] + '_reverse'
	elif transcript_instance.__dict__['strand'] == '1':
	    output_name = transcript_instance.__dict__['transcript_id']
        with open(output_name, 'w') as output_file:
            exon_dictionary = transcript_instance.__dict__['exons']
            for k,v in exon_dictionary.iteritems():
	        if int(v[0]) or int(v[1]) != 0:
                    plus_50 = int(v[1]) + 50
                    minus_50 = int(v[0]) - 50
                    output = k + ',' + v[0] + ',' + v[1] + ',' + str(minus_50) + ',' + str(plus_50) + '\n'
                    output_file.write(output)
	return output_name

    def sorter(self, file):
	print 'sorting interval_file : ' + file
	if 'reverse' in file:
	    command = ["sort", "-r", "-V", file]
	else:
	    command = ["sort", "-V", file]
	output = file +'.intervals'
	with open(output, 'w') as sorted_file:
	    process = subprocess.Popen(command, stdout=subprocess.PIPE)
	    sorted_output = process.communicate()[0]
	    sorted_file.write(sorted_output)
            #remove_command = ['rm', file]
            #subprocess.call(remove_command)
	 
	return output

    def match_sample_column_header(self, opened_coverage_file, exome_identifier):
	y = 'Depth_for_' + exome_identifier
	header_list = opened_coverage_file.readline().split()
	for i,x in enumerate(header_list):
	    if x == y:
		result = [i,x]
	return result	 

    def line_search_and_split(self, file, current_start, current_end):
        seek_pointer = file.seek(((current_end + current_start)/2),0)
	print 'SEEKER ' + str(file.tell())
        partial_line = file.readline()
        whole_line = file.readline()
        split_line = whole_line.split()
        return split_line


    def bin_search(self, locus_array, coverage_file, exome_identifier):
        in_file = {}
        not_in_file = []
        pos_iter_array = []
        neg_iter_array = []
	#locus_array = [['16', '86544126']]
	output = [in_file, not_in_file]
        with open(coverage_file, 'r') as coverage_file:
	    header_index = self.match_sample_column_header(coverage_file, exome_identifier)
	    items_checked = 0
	    this_item = 0
	    desired = 1
	    for item in locus_array:
	        this_item += 1
	 	last_target_locus = []
		end_array = []
		begin_array = [0]
		seek_end = coverage_file.seek(0,2)
		end_array.append(coverage_file.tell())
		while items_checked < this_item:
		    this_begin = begin_array[-1]
		    this_end = end_array[-1]
		    next_line = self.line_search_and_split(coverage_file, this_begin, this_end)
		    print next_line
		    #perhaps include number of characters in chromosome to avoid match between e.g. 6: and 16:
		    if ':' in next_line[0]:
			print
			print next_line[0]
			split_locus = split_locus = next_line[0].split(':')
			chrom = int(item[0])
			locus = int(item[1])
			target_chrom = int(split_locus[0])
		        target_locus = int(split_locus[1])
			#print 'chrom: ' + str(chrom) 
			#print 'locus: ' + str(locus)
			#print 'target_chrom: ' + str(target_chrom)	
			#print 'target_locus: ' + str(target_locus)
			#print 'current_begin ' + str(this_begin)
			#print 'current_end ' + str(this_end)
			#print 'current_pointer_location ' + str(coverage_file.tell())
			#print
			if chrom > target_chrom:
			    print
			    print 'chrom greater, move start to current'
			    begin_array.append(coverage_file.tell())
			elif chrom < target_chrom:
			    print
			    print 'chrom less, move end to current'
			    end_array.append(coverage_file.tell())
			elif chrom == target_chrom:
			    print
			    print 'FOUND TARGET CHROMOSOME'
			    last_target_locus = [target_locus]
			    #print 'last_target_locus ' + str(last_target_locus[-1])
			    chrom_begin_array = [begin_array[-1]]
			    #print 'cba ' + str(chrom_begin_array)
			    chrom_end_array = [end_array[-1]]
			    #print 'cea ' + str(chrom_end_array)
			    items_checked += 1
			    while locus != last_target_locus[-1]:
				print
				print 'TARGET LOCUS NOT A MATCH'
				new_next_line = self.line_search_and_split(coverage_file, chrom_begin_array[-1], chrom_end_array[-1])
				new_target = new_next_line[0].split(':')
				new_target_chrom = int(new_target[0])
				new_target_locus = int(new_target[1])
				#print 'desired locus ' + str(item)
				#print 'new line ' + str(new_next_line)
				#print 'new_target ' + str(new_target)
				#print 'current_coords ' + str(chrom_begin_array) + ' ' + str(chrom_end_array)
				#print 'new_target_chrom ' + str(new_target_chrom)
				#print 'new_target_locus ' + str(new_target_locus)
				#print 'updating intervals to search for locus'
				#print 'current pointer ' + str(coverage_file.tell())
				#check chromosome is still the same
				if chrom < new_target_chrom:
				    print
				    print 'THIS CHROMOSOME NOW GREATER THAN DESIRED'
				    #move the end to the current location
				    chrom_end_array.append(coverage_file.tell())
				if chrom > new_target_chrom:
				    print
				    print 'THIS CHROMOSOME NOW LESS THAN DESIRED'
				    #move the start to current location
				    chrom_begin_array.append(coverage_file.tell())
				if chrom == new_target_chrom:
				    print
				    print 'CHROMOSOME STILL MATCHES'
				    if locus > new_target_locus:
					print 'THIS LOCUS NOW LESS THAN DESIRED'
					chrom_begin_array.append(coverage_file.tell())
					if chrom_begin_array[-1] == chrom_begin_array[-2]:
					    print 'END OFFSET REQUIRED'
					    chrom_end_array.append(chrom_end_array[-1] - 10)
				    elif locus < new_target_locus:
					print
					print 'THIS LOCUS NOW GREATER THAN DESIRED'
					chrom_end_array.append(coverage_file.tell())
					if chrom_end_array[-1] == chrom_end_array[-2]:
					    #need to create an offset
					    print 'BEGIN OFFSET REQUIRED'
					    chrom_begin_array.append(chrom_begin_array[-1] - 10)
				    elif locus == new_target_locus:
					print
					print 'MATCH'
					coverage_data = new_next_line[header_index[0]]
					in_file[locus] = coverage_data
					last_target_locus.append(new_target_locus)
					items_checked += 1 
	return output


    def binary_search_coverage(self, locus_array, coverage_file, exome_identifier):
        in_file = {}
        not_in_file = []
        pos_iter_array = []
	neg_iter_array = []
        output = [in_file, not_in_file]
        with open(coverage_file, 'r') as coverage_file:
	#extract_headerlist here to deduce column to extract coverage_data
	    header_index = self.match_sample_column_header(coverage_file, exome_identifier)
            items_checked = 0
            this_item = 0
            for item in locus_array:
		print item
                this_item += 1
                last_target_locus = []
                end_array = []
                begin_array = [0]
                coverage_file.seek(0,2)
                end_array.append(coverage_file.tell())
                while items_checked < this_item:
                    this_begin = begin_array[-1]
                    this_end = end_array[-1]
                    coverage_file.seek(((this_end + this_begin)/2),0)
                    partial_line = coverage_file.readline()
                    after_partial = coverage_file.tell()
                    coverage_file.seek(after_partial)
                    whole_line = coverage_file.readline()
		    print whole_line
                    split_line = whole_line.split()
                    if ':' in split_line[0]:
			print whole_line
                        split_locus = split_line[0].split(':')
                        chrom = int(item[0])
                        target_chrom = int(split_locus[0])
                        locus = int(item[1])
                        target_locus = int(split_locus[1])
                        if chrom == target_chrom:
			    print whole_line
                            last_target_locus = [target_locus]
			    print last_target_locus
			    print locus
                            chrom_end_array = [end_array[-1]]
                            chrom_begin_array = [begin_array[-1]]
                            neg_iter = 0
                            pos_iter = 0
                            while locus != last_target_locus[-1]:
                                coverage_file.seek(((chrom_end_array[-1] + chrom_begin_array[-1])/2),0)
                                partial_line2 = coverage_file.readline()
                                end_partial2 = coverage_file.tell()
                                coverage_file.seek(end_partial2)
                                whole_line2 = coverage_file.readline()
                                split_line2 = whole_line2.split()
                                split_locus2 = split_line2[0].split(':')
                                target_chrom2 = int(split_locus2[0])
                                target_locus2 = int(split_locus2[1])
				print target_chrom2
                                if chrom == target_chrom2:
                                    if locus == target_locus2:
					#extract coverage_data
					coverage_data = split_line2[header_index[0]]
                                        #in_file.append([locus, coverage_data])
					in_file[locus] = coverage_data
                                        last_target_locus.append(target_locus2)
                                        items_checked += 1
                                        if neg_iter > 1:
                                            neg_iter_array.append(neg_iter)
                                        if pos_iter > 1:
                                            pos_iter_array.append(pos_iter)
                                    elif locus < target_locus2:
                                        chrom_end_array.append(coverage_file.tell())
                                        if chrom_end_array[-1] == chrom_end_array[-2]:
                                            chrom_begin_array.append(chrom_begin_array[-1] - 1)
                                            neg_iter += 1
                                            if neg_iter >= 200:
                                                not_in_file.append(locus)
                                                last_target_locus.append(locus)
                                                items_checked += 1
                                                neg_iter_array.append(neg_iter)
                                    elif locus > target_locus2:
                                        chrom_begin_array.append(coverage_file.tell())
                                        if chrom_begin_array[-1] == chrom_begin_array[-2]:
                                            chrom_end_array.append(chrom_end_array[-1] + 1)
                                            if pos_inter >= 200:
						not_in_file.append(locus)
						last_target_locus.append(locus)
                                                items_checked += 1
                                                pos_iter_array.append(pos_iter)
                                elif chrom > target_chrom2:
                                    #move beginning to current_location
                                    chrom_begin_array.append(coverage_file.tell())
                                    #reset the end to the one before it starts repeating
                                    if chrom_end_array[-2] == chrom_end_array[-1] - 1:
					print '> resetting'
                                        end_iter1 = 2
                                        end_iter2 = 1
                                        while chrom_end_array[-iter1] == chrom_end_array[-iter2] - 1:
                                            end_iter1 += 1
                                            end_iter2 += 2
                                        chrom_end_array.append(end_iter1)
                                    else:
					print '> deleting'
					print chrom_end_array[-1]
                                        del chrom_end_array[-1]
                                elif chrom < target_chrom2:
                                    #move end to current location
                                    chrom_end_array.append(coverage_file.tell())
                                    #reset the begining to before it starts repeating
                                    if chrom_begin_array[-2] == chrom_begin_array[-1] - 1:
					print '< resetting'
                                        begin_iter1 = 2
                                        begin_iter2 = 1
                                        while chrom_beign_array[-iter1] == chrom_begin_array[-iter2] - 1:
                                            begin_iter1 += 1
                                            begin_iter2 += 2
                                        chrom_begin_array.append(begin_iter1)
                                    else:
					print '< deleting'
					print chrom_begin_array[-1]
                                        del chrom_begin_array[-1]
                        elif chrom > target_chrom:
                            #move begining to current_location
                            begin_array.append(coverage_file.tell())
                        elif chrom < target_chrom:
                            #move end to current_location
                            end_array.append(coverage_file.tell())
        return output

    #where binary_search_output is [{infile locus : coverage} , [not in file locus]]
    def plottable_genomic_data(self, binary_search_data, range_array, exome_identifier, transcript_instance):
	filename = exome_identifier + '_' + transcript_instance.gene_symbol + '.plottable.coverage'
	with open(filename, 'w') as genomic_for_plotting:
	    no_chrom_range_array = []
	    count = -1
	    in_file_loci = binary_search_data[0].keys()
	    for chrom_locus in range_array:
	        no_chrom_range_array.append(chrom_locus[1])
	    for item in no_chrom_range_array:
		if int(item) in in_file_loci:
		    count += 1
		    genomic_for_plotting.write(str(count) + ',' + str(binary_search_data[0][int(item)] + '\n'))
		elif int(item) not in in_file_loci and int(item) in binary_search_data[1]:
		    count += 1 
		    genomic_for_plotting.write(str(count) + ',0' + '\n')
	return str(filename)


class Argument_handler(Coverage_parser, Gnuplotter):
    def __init__(self, s=None, sample_file=None, g=None, gene_file=None):
	if s and sample_file:
	    argument_list = [str(s), str(sample_file), str(g), str(gene_file)]
            this_parser = self.create_parser()
            arguments, unknown = this_parser.parse_known_args(argument_list)
	else:
	    this_parser = self.create_parser()
            arguments, unknown = this_parser.parse_known_args()
        self.arg_dict = vars(arguments)
        print 'initialised exome coverage parser with: ' + str(self.arg_dict)

    def create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', action='store', dest='sample_names', help='path to file containing exome samples to be analysed')
        parser.add_argument('-g', action='store', dest='gene_names', help='path to file containing the genes to be analysed')
        return parser

    #handle if no sample path is given nonetype error
    def handler(self):
        switch = 0
        if 'sample_names' in self.arg_dict.keys() and os.path.isfile(self.arg_dict['sample_names']):
            print 'samples file location confirmed. Ensure one sample per line.'
            switch += 1
        elif not os.path.isfile(self.arg_dict['sample_names']):
            print 'Cannot find samples file check path or add -s flag before path'
        if 'gene_names' in self.arg_dict.keys() and os.path.isfile(self.arg_dict['gene_names']):
            print 'genes file location confirmed. Ensure one sample per line.'
            switch += 1
        elif not os.path.isfile(self.arg_dict['sample_names']):
            print 'Cannot find smaples file check path or add -g flag before path'
        if switch == 2:
#           call rest of program
            instance = Coverage_parser(self.arg_dict['sample_names'], self.arg_dict['gene_names'], '/mnt/Data1/resources/alamut-genes/grch37.txt')
            list_coverage_file_dicts = instance.exome_coverage_finder_bash()
            instance.find_gene_intervals()
            longest_transcript_list = instance.longest_transcript()
            for item in longest_transcript_list:
                output_name = instance.exon_interval_file_creator(item)
                sorted_file = instance.sorter(output_name)
                transcript_range = instance.generate_transcript_range(sorted_file, item)
                for sample_coverage_file in list_coverage_file_dicts:
                    for k,v in sample_coverage_file.iteritems():
			print k,v 
			print 'starting binary search'
                        #binary_search_output = instance.binary_search_coverage(transcript_range, v, k)
			binary_search_output = instance.bin_search(transcript_range, v, k)
			print 'generating plottable data'
			print len(binary_search_output[0])
                        x = instance.plottable_genomic_data(binary_search_output, transcript_range, k, item)
                        extended = str(sorted_file) + '.extended'
			print len(transcript_range)
                        exons = str(sorted_file) + '.exons'
                        gnuplot_instance = Gnuplotter(exons, extended, x, k, item.gene_symbol, str(len(transcript_range)))
                        gnuplot_instance.coverage_plot()

        else:
            print 'ERROR - Input criteria not satisfied.'


if __name__ == '__main__':	    
    print 'main'
    A = Argument_handler()
    A.handler()
	
