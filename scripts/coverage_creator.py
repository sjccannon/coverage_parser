import argparse, os, subprocess, fnmatch, Gnuplot, Gnuplot.funcutils

#the following code can be execute with 
#python coverage_creator.py -s sample_file -g gene_file
#and will produce a coverage plot for each gene for every sample.

#Models a transcript using data from the Alamut genes file 
class Gnuplotter():
    def __init__(self, interval_exons, interval_extended, plottable_coverage, exome_identifier, gene, length_of_extended_transcript):
        self.interval_exons = interval_exons
        self.interval_extended = interval_extended
        self.plottable_coverage = str(plottable_coverage)
	self.exome_identifier = exome_identifier
	self.gene = gene
	self.length_of_extended_transcript = length_of_extended_transcript

    #funtion to plot each coverage plot, uses gnuplot wrapper 
    def coverage_plot(self):
	g = Gnuplot.Gnuplot(debug=1)
	g('set terminal png size 4000, 1000')
        #file_name = str(self.gene) + '.png'
	output = 'set output ' + '"' + str(self.exome_identifier) + '_' + str(self.gene) + '.png' + '"'
	cut_off_20x = "set object rect from 0,0 to " + str(self.length_of_extended_transcript) + ",0.275 fc rgb 'grey' fs solid 0.3"
	g(output)
	g("set datafile separator ','")
	g('set style line 1 lt 1 lw 2 lc 3')
	g("set style line 2 lt 2 lw 10 lc rgb 'navy'")
	g("set style line 3 lt 3 lw 3 lc rgb 'black'")
	g("set title " + "'" + str(self.gene) + "'" + " font  ',28'" )
	g("set object rect from 0,0 to " + str(self.length_of_extended_transcript) + ",0.275 fc rgb 'grey' fs solid 0.3")
	g('set xrange [0:' + str(self.length_of_extended_transcript)  + ']')
        g("set ytics nomirror out")
	g("set xtics nomirror out")
	g("set xtics rotate")
	g("set xlabel 'nucleotides' offset 0,-2 font ',22'")
	g("set ylabel 'Coverage' offset -1,0 font ',22'")
	g("set tics font ', 18'")
	g("set grid xtics front")
	g("min(a,b) = (a < b) ? a : b")
	g("f(x) = min(1.0, (log(x + 10.0) - log(10.0)) / 4.0)")
	g("set ytics ('0' f(0), '5' f(5), '10' f(10), '20' f(20), '40' f(40), '100' f(100), '200' f(200), '400' f(400), '800' f(800), '1600' f(1600))")
	string_alternative = str(self.plottable_coverage)
	    #final plot command
        g('plot ' + '"' + string_alternative + '"' + ' using 1:(f($2)) with lines ls 3 title "", -0.08 title "", "' + str(self.interval_exons) + '" using 1:2:xtic(4) with lines ls 2 title "", "' + str(self.interval_exons) + '" using 1:2:3 with labels offset 0,char 1 title "", "' + str(self.interval_extended) + '" using 1:2:xtic(3) with lines ls 1 title ""')

#models the transcript as supplied in the alamut database file
class Transcript():

    def __init__(self, alamut_line):
        self.alamut_line = alamut_line
	self.gene_symbol = self.alamut_line[1]
        self.transcript_id = self.alamut_line[7]
        self.cds_start = self.alamut_line[10]
        self.cds_end = self.alamut_line[11]
        self.cds_length = int(self.cds_end) - int(self.cds_start) + 1
        self.chromosome = self.alamut_line[3]
	self.strand = self.alamut_line[6]
        self.gene_start = self.alamut_line[4]
        self.gene_stop = self.alamut_line[5]
        self.exons = {self.alamut_line[12] : [self.alamut_line[15], self.alamut_line[16]]}

    #funtion to generate the transcript range, exon range and intron ranges.
    #that is, coding exons +/- 50bps
    #These are then plotted as two data series.
    #also detects forward or reverse strand and rvereses as appropriate for plotting
    #returns an array of the ranges
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
	    cumulative_interval_count = -1
	    for item in extended:
		extension = 0
		exon_length = item - 100
		end_of_exon = item - 50
		for i in range(int(item)):
		    count1 += 1
		    extension += 1
		    if extension <= 50:
		        cumulative_interval_count += 1
			if cumulative_interval_count == 0 or cumulative_interval_count % 50 == 0:
		            extended_interval_file.write(str(count1)+',-0.06," "\n')
			else:
			    extended_interval_file.write(str(count1)+',-0.06,\n')
		    elif extension > 50 and extension <= end_of_exon:
			extended_interval_file.write('\n')
		    elif extension > end_of_exon:
			cumulative_interval_count += 1
			if count1 == len(range_array):
			    extended_interval_file.write(str(count1)+',-0.06," "\n')
			else:
			    extended_interval_file.write(str(count1)+',-0.06,\n')
	exon_file_name = input_file + '.exons'
	with open(exon_file_name, 'w') as exon_interval_file:
	    cumulative_exon_length = 0
	    reverse_cumulative_exon_length = sum(exons) + 1
	    print reverse_cumulative_exon_length
	    count2 = 0
	    exon_count = 0
	    reverse_exon_count = len(transcript_instance.exons)
	    for item in extended:
		exon_count += 1
		extension2 = 0
		exon_length = item - 100
		exon_middle = exon_length/2
		end_of_exon = item - 50
		for i in range(int(item)):
		    count2 += 1
		    extension2 += 1
		    if extension2 <= 50:
		        exon_interval_file.write('\n')
		    elif extension2 > 50 and extension2 <= end_of_exon:
			cumulative_exon_length += 1
			reverse_cumulative_exon_length -= 1
			#add exon numbering
			if extension2 == exon_middle + 50:
			    if transcript_instance.__dict__['strand'] == '-1':
			        exon_interval_file.write(str(count2) + ',-0.06,' + str(reverse_exon_count) + '\n'), 
				reverse_exon_count -= 1
			    else:
			        exon_interval_file.write(str(count2) + ',-0.06,' + str(exon_count) + ',' + '\n')
			#add start and stop cdna
			elif extension2 == 51 or extension2 == end_of_exon:
				print exon_length
			    #if transcript_instance.__dict__['strand'] == '-1':
			        if exon_length < 50:
				    if extension2 == 51 and transcript_instance.__dict__['strand'] == '1':
			                exon_interval_file.write(str(count2) + ',-0.06,,' + str(cumulative_exon_length) + '\n')
				    if extension2 == end_of_exon and transcript_instance.__dict__['strand'] == '-1':
				        exon_interval_file.write(str(count2) + ',-0.06,,' + str(reverse_cumulative_exon_length) + '\n')
			        else:
				    if transcript_instance.__dict__['strand'] == '1':
				        exon_interval_file.write(str(count2) + ',-0.06,,' + str(cumulative_exon_length) + '\n')
				    elif transcript_instance.__dict__['strand'] == '-1':
					exon_interval_file.write(str(count2) + ',-0.06,,' + str(reverse_cumulative_exon_length) + '\n')
			else:
			    exon_interval_file.write(str(count2) + ',-0.06,,' + '\n')
		    elif extension2 > end_of_exon:
		        exon_interval_file.write('\n')
        return range_array

#the coverage parser object returns the transcript instances and coveage metric files to be interrogated.  
class Coverage_parser(Transcript):

    transcript_instances = []
    exome_coverage_files = ''
    
    #init takes sample names, gene names into memory
    def __init__(self, sample_name_file, gene_name_file, alamut_file):
        self.sample_list = self.list_from_file(sample_name_file)
        self.gene_list = self.list_from_file(gene_name_file)
	self.alamut_file = alamut_file
	assert os.path.isfile(self.alamut_file), 'Alamut file is not in specified location'

    #funtion to quickly strip and split lines form input file
    def line_strip_split(self, line):
        line = line.strip('\n')
        split_line = line.split()
        return split_line

    #turn a file into a 2d array where each line is an array 
    def list_from_file(self, input_file):
        new_list = []
        with open(input_file, 'r') as inputfile:
            for line in inputfile:
                line = line.strip()
                new_list.append(line)
        return new_list

    #uses accompanying bash script to identify the required coverage file
    #much faster than a python equivalent
    def exome_coverage_finder_bash(self):
	exome_coverage_files = []
        print 'finding coverage files for : '
        print (self.sample_list)
	sample_iteration = 0
   	for exome_sample in self.sample_list:
	    exome_sample = exome_sample.strip('\n')
	    coverage_dict = {}
	    try:
	        command = ["bash", "all_exome_coverage_files", exome_sample]
	        process = subprocess.Popen(command, stdout=subprocess.PIPE)
	        cov_file_path = process.communicate()[0].strip('\n')
	        #communicate output
	        coverage_dict[exome_sample] = cov_file_path
                exome_coverage_files.append(coverage_dict)
                self.exome_coverage_files = exome_coverage_files
                assert len(exome_coverage_files) > 0, 'No exome coverage file identified by bash script, coverage connot be plotted'
            except:
                print('exome coverage finder error, ensure bash script all_exome_coverage_files in same directory as execution')
        return exome_coverage_files

    #finds the intervals for each gene and intitialises a transcript instance.
    def find_gene_intervals(self):
        lines_parsed = 0
        checked_genes = []
        with open(self.alamut_file, 'r') as alamut_file:
            for line in alamut_file:
                for gene in self.gene_list:
                    #if its the first line
                    if gene in line and len(self.transcript_instances) == 0:
                        line = line.split()
			if gene == line[1] or gene == line[7]:
                            initial_transcript_instance = Transcript(line)  
			    self.transcript_instances.append(initial_transcript_instance)
                            checked_genes.append(gene)
		    elif gene in line and len(self.transcript_instances) > 0:
		        line = line.split()
			#if gene is symbol or transcript
			if gene == line[1] or gene == line[7]:
			    if self.transcript_instances[-1].transcript_id == line[7] and line [12] not in self.transcript_instances[-1].exons:
			        self.transcript_instances[-1].exons[line[12]] = [line[15], line [16]]
			    if self.transcript_instances[-1].transcript_id != line[7]:
			        additional_transcript_instance = Transcript(line)
			        self.transcript_instances.append(additional_transcript_instance)
                                checked_gene.append(gene)
        for gene in gene_list:
            if gene not in checked_genes:
                print gene + ' not found in alamut_file, check gene nomenclature for synonyms, remove form analysis or update alamut file'

    #returns the longeest transcript from those available
    def longest_transcript(self):
        longest_transcripts = []
	current_longest = []
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
        print 'the transcripts to be analysed are:'
        for item in longest_transcripts:
            print str(item.__dict__['gene_symbol']) + ' ' + str(item.__dict__['transcript_id']) + '\n'
        return longest_transcripts

    #takes transcript instance and creates output file 
    def exon_interval_file_creator(self, transcript_instance):
        #print 'creating exon interval files : ' + transcript_instance.__dict__['transcript_id']
	if transcript_instance.__dict__['strand'] == '-1':
	    output_name = transcript_instance.__dict__['transcript_id'] + '_reverse'
	elif transcript_instance.__dict__['strand'] == '1':
	    output_name = transcript_instance.__dict__['transcript_id']
        else:
            print "No strand information for transcript, output name is foreward by default"
            output_name = transcript_instance.__dict__['transcript_id']
        with open(output_name, 'w') as output_file:
            exon_dictionary = transcript_instance.__dict__['exons']
            assert not bool(exon_dict), 'There are no exons in this transcript, check columns of alamut file align with transcript class'
            for k,v in exon_dictionary.iteritems():
	        if int(v[0]) or int(v[1]) != 0:
                    plus_50 = int(v[1]) + 50
                    minus_50 = int(v[0]) - 50
                    output = k + ',' + v[0] + ',' + v[1] + ',' + str(minus_50) + ',' + str(plus_50) + '\n'
                    output_file.write(output)
	return output_name

    #funciton to sort files as requried for forward or reverse plotting of transcript coordinates
    def sorter(self, file):
	if 'reverse' in file:
	    command = ["sort", "-r", "-V", file]
	else:
	    command = ["sort", "-V", file]
	output = file +'.intervals'
	with open(output, 'w') as sorted_file:
	    process = subprocess.Popen(command, stdout=subprocess.PIPE)
	    sorted_output = process.communicate()[0]
	    sorted_file.write(sorted_output)
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
        partial_line = file.readline()
        whole_line = file.readline()
        split_line = whole_line.split()
        return split_line

    def output_iterations(self, iteration, locus):
	if iteration == 20:
	    with open("iteration_file", "a") as outfile:
	        outfile.write(str(iteration) + '\t' + str(locus) + '\n')

    #binary search to enable rapid look up from coverage file.
    #first pass searches based on chromosome
    #second pass searches based on coordinate
    #ranges are adjusted as required, one search for each target locus
    #byte offset requried to account for reading from centre of line  
    def bin_search(self, locus_array, coverage_file, exome_identifier):
        in_file = {}
        not_in_file = []
	output = [in_file, not_in_file]
        #opens target coverage file into memory
        with open(coverage_file, 'r') as coverage_file:
        #finds the headers
	    header_index = self.match_sample_column_header(coverage_file, exome_identifier)
	    items_checked = 0
	    this_item = 0
	    #iterates through locus targets required
	    for item in locus_array:
	        this_item += 1
	    #arrays to define lookup logic i.e. when to move through loop
	 	last_target_locus = []
		end_array = []
		begin_array = [0]
		#find the end of the file 
		seek_end = coverage_file.seek(0,2)
		end_array.append(coverage_file.tell())
		#switch to account for when all the searches have been completed 
		while items_checked < this_item:
		    start_iter = 0
		    end_iter = 0
		    this_begin = begin_array[-1]
		    this_end = end_array[-1]
		    #check the data in the line
		    next_line = self.line_search_and_split(coverage_file, this_begin, this_end)
		    if ':' in next_line[0]:
			split_locus = split_locus = next_line[0].split(':')
			chrom = int(item[0])
			locus = int(item[1])
			target_chrom = int(split_locus[0])
		        target_locus = int(split_locus[1])
		    #logic to define if target chromosome and adjust start and end coordianates
			if chrom > target_chrom:
			    begin_array.append(coverage_file.tell())
			elif chrom < target_chrom:
			    end_array.append(coverage_file.tell())
			#if correct chromosome, redefine the start and end
			elif chrom == target_chrom:
			    last_target_locus = [target_locus]
			    chrom_begin_array = [begin_array[-1]]
			    chrom_end_array = [end_array[-1]]
			    #switch to check that the last searched locus hasn't been found
			    while locus != last_target_locus[-1]:
				new_next_line = self.line_search_and_split(coverage_file, chrom_begin_array[-1], chrom_end_array[-1])
				new_target = new_next_line[0].split(':')
				new_target_chrom = int(new_target[0])
				new_target_locus = int(new_target[1])
				#check chromosome is still the same, keeps the start and end byte sizes correct
				if chrom < new_target_chrom:
				    #move the end to the current location
				    chrom_end_array.append(coverage_file.tell())
				if chrom > new_target_chrom:
				    #move the start to current location
				    chrom_begin_array.append(coverage_file.tell())
				if chrom == new_target_chrom:
				    if locus > new_target_locus:
					chrom_begin_array.append(coverage_file.tell())
					#identifies when the partial is the required line
					if chrom_begin_array[-1] == chrom_begin_array[-2]:
					    chrom_end_array.append(chrom_end_array[-1] - 10)
					    start_iter += 1
					    if start_iter == 40:
						#capture_locus
						not_in_file.append(locus)
						#exit_loops
						last_target_locus.append(locus)
						items_checked += 1
				    elif locus < new_target_locus:
					chrom_end_array.append(coverage_file.tell())
					#identifies when the partial is the required line
					if chrom_end_array[-1] == chrom_end_array[-2]:
					    chrom_begin_array.append(chrom_begin_array[-1] - 10)
					    end_iter += 1
					    if end_iter == 40:
						not_in_file.append(locus)
						last_target_locus.append(locus)
						items_checked += 1
				    elif locus == new_target_locus:
					coverage_data = new_next_line[header_index[0]]
					in_file[locus] = coverage_data
					#exit loops 
					last_target_locus.append(new_target_locus)
					items_checked += 1
	return output

    #where binary_search_output is [{infile locus : coverage} , [not in file locus]]
    #writes to a plottable coverage file. This is another data series plotted in addition to the exon target files
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
    
    #remove intemediate files
    def clean_up(self, target_directory=None):
	for file in os.listdir(os.getcwd()):
	    if file.startswith("NM_") or file.endswith("plottable.coverage"):
		remove_command = ["rm", file]
		subprocess.call(remove_command)

#models the input arguments and calls the program if all inputs are satisfied
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
            #call rest of program
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
			print 'generating plottable data '
			print 'length bin search ' + str(len(binary_search_output[0]))
                        x = instance.plottable_genomic_data(binary_search_output, transcript_range, k, item)
                        extended = str(sorted_file) + '.extended'
			print 'length transcript range ' + str((len(transcript_range)))
                        exons = str(sorted_file) + '.exons'
                        gnuplot_instance = Gnuplotter(exons, extended, x, k, item.gene_symbol, str(len(transcript_range)))
                        gnuplot_instance.coverage_plot()
#	    instance.clean_up()

        else:
            print 'ERROR - Input criteria not satisfied. Please check data files have one sample/gene per line'

if __name__ == '__main__':	    
    A = Argument_handler()
    A.handler()
	
