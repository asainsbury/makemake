import re,os,sys,os.path,errno,glob
from pprint import pprint
import pandas as pd
from netaddr import *
import functools
import logging
from pathlib import Path
import numpy as np

home = str(Path.home())
path1 = "{}/{}".format(home,"/projects/scripts/custom_functions")

''' Append paths as you add more custom stuff '''
sys.path.append(path1)


import log_error as setup


def world():
    '''
    Test function
    '''
    print("Hello, World!")



class bgp_table(object):

    def __init__(self, host, route_table, peer_data, log_level):

        self.host           = host
        self.route_table    = route_table
        self.peer_data      = peer_data
        self.log_level      = log_level

        
        self.run_log_test(self.log_level)
        self.run_input_test(self.route_table, self.host)


    def __repr__(self):
        return("{}: {}".format("Route Table", self.log_level, self.host))

    ################################# tests #############################################
    
    def run_log_test(self, log_level):
        if re.search('debug|info|warning|error|critical', log_level, re.IGNORECASE):
            pass
        else:
            setup.log_collector.write_msg('error',"Error processing log level", log_level)
            exit(0)

    def run_input_test(self, route_table, peer_data):
        if isinstance(route_table, list):
            setup.log_collector.write_msg(self.log_level,"Running checks", 'PASS')
        elif isinstance(peer_data, dict):
            setup.log_collector.write_msg(self.log_level,"Running checks", 'PASS')
        else:
            setup.log_collector.write_msg("warning","Error must pass in a list", '{} {}'.format(type(self.route_table), self.host))

    ################################# gravy #############################################

    def total_routes(self):
        footer  = re.findall(r'Total number.*', str(self.route_table), re.IGNORECASE)
        footer  = re.sub(r'\[|\]|\'', '', str(footer))
        
        if footer:
            setup.log_collector.write_msg(self.log_level,"Finding Totals", 'PASS')
            return(footer.split()[-1])
        else:
            setup.log_collector.write_msg(self.log_level,"Finding Totals", 'FAIL')
            return(None)


    def get_rid(self):
        rid     = re.findall(r'local router.*', str(self.route_table),  re.IGNORECASE)
        rid     = re.sub(r'\[|\]|\'|,', '', str(rid))

        if rid:
            setup.log_collector.write_msg(self.log_level,"Finding RID", 'PASS')
            return(rid.split()[4])
        else:
            setup.log_collector.write_msg(self.log_level,"Finding RID", 'FAIL')
            return(None)


    def get_BGP_table_version(self):
        ver     = re.findall(r'table version.*', str(self.route_table),  re.IGNORECASE)
        ver     = re.sub(r'\[|\]|\'', '', str(ver))
        ver     = ver.split(',')[0].split()

        if ver:
            setup.log_collector.write_msg(self.log_level,"Finding Table", 'PASS')
            return(ver[-1])
        else:
            setup.log_collector.write_msg(self.log_level,"Finding Table", 'FAIL')
            return(None)


    # def get_default(self):
    #     other   = re.findall(r'default|Distinguisher.*', str(self.route_table))
        
    #     if other:
    #         setup.log_collector.write_msg(self.log_level,"Finding default", 'PASS')
    #         return(other)
    #     else:
    #         setup.log_collector.write_msg(self.log_level,"Finding default", 'FAIL')
    #         return(None)

    # def get_header(self):
    #     header      = re.findall(r'Next Hop', str(self.route_table))    
    #     header      = header.replace('Next Hop', 'Next_Hop')

    #     if header:
    #         setup.log_collector.write_msg(self.log_level,"Finding Header", 'PASS')
    #         return(header)
    #     else:
    #         setup.log_collector.write_msg(self.log_level,"Finding Header", 'FAIL')

    ################################# meat #############################################


    @setup.exception
    def parse_table(self):
        '''
        This method takes care of the multiline format returned by IOS L3 devices.

        One thing not being done here, is down filling a BGP route which is not the valid route.
        In a regular full BGP table, mulitple paths to a destination route exist and are represented with blanks.
        So this is a future update, as this is being ignored here.
        '''

        network = []
        result  = []

        data    = self.route_table
        host    = self.host
        total   = self.total_routes()
        rid     = self.get_rid()
        ver     = self.get_BGP_table_version()

        # pprint(data)

        for c, line in enumerate(data):

            # Parse the route table, only looking for valid routes
            # This would break on a BGP table with multiple paths to the same destination
            # as that is missing the regex pattern match.
            # This needs to be fixed by the previous method.
            if re.search("\d+\.\d+\.\d+\.\d+", line) and not re.search("router|default|family", line, re.IGNORECASE):
                network.append(line)
                # print(line)

                # Do a join on truncated routes
                # Mark the route with a hash at the end of it for future regex
                if re.search('^\s+\d+\.\d+\.\d+\.\d+', line):
                    del network[-2:]
                    before  = c -1
                    new     = '{} {}#'.format(data[before],line.strip())
                    network.append(new)


        
        result = (self.format_bgp_route(host, rid, ver, network, self.peer_data))
        '''
        The length tests only work if cisco print out the totals, so have dropped them for now.
        '''
        # self.test_length(len(network), len(result), total)
        # setup.log_collector.write_msg(self.log_level,"Route Check", '{}'.format("PASS"))

        return(result)


    @setup.exception
    def find_deliminator(self, line, count):
        '''
        Recursive function to find the nearest space to index[xx]
        As this should be a space, and marks where we can split up the string into 2 elements.
        '''

        if line[count].isspace():
            return(count)

        else:
            return(self.find_deliminator(line, (count + 1)))


    @setup.exception
    def format_bgp_route(self, host, rid, ver, routes, peer_data):
        '''
        When I have time to nicely format the debugging for this....
        This is where it all goes wrong, if you have an edge case value.

        So, this dude is better at splitting up the already slightly touched up line into 
        data we can assign to values with keys. 

        I did a lot of hacking about with a pattern in the first instance, look at the git history
        for more info, but I mangaged to finally spot the magic pattern and work off that.

        We break the line up into 2 parts, the start and the end, on around the 50'th char, 
        which neatly allows a bit of logic to then break up each section into the correct segments.

        Cisco is terrible at the text formatting, and this was a decent challenge. 

        Basically have to ignore case in all instances,  

        '''
        # print(type(routes))
        # pprint(routes)
        
        output      = []
        host_data   = ('{} {} {}'.format(host, rid, ver))
        host_data   = host_data.split()
     
        for line in routes:

            d       = {}
            delim   = (self.find_deliminator(line, 50))
            start   = line[:delim].lstrip()
            end     = line[delim:]

            elements = start[3:].split()
            prefix   = elements[0]
            nexthop  = elements[1]

            # print(delim)
            # pprint('{}##{}'.format(start, end))
            # pprint(end)
            # pprint(elements)
            # pprint(len(elements))

            if len(elements) > 2:
                d['Metric'] = elements[2]

            d['HOST']       = host
            d['RID']        = rid
            d['TABLE']      = ver
            d['Status']     = start[:3]
            d['Network']    = prefix
            d['Next_Hop']   = nexthop

            parts           = end.split()
            d['Origin']     = parts.pop(-1)

            # print(host)
            # print('\n\n{}\n{}'.format(host,line))
            # print('{} {}'.format(start, parts))

            if re.match(r'0|32768', parts[0]):
                d['Weight'] = parts.pop(0)


                if parts:
                    # Probably better with a join but it keeps the list format this way
                    # And to do some error checking on the stuff inside the path, so if it
                    # has a 0 int we have failed the pattern match, and we should print out
                    # and error to the log
                    # pprint('##{}##'.format(parts))
                    d['Path']   = str(parts)

            else:
                d['LocPrf'] = parts.pop(0)
                d['Weight'] = parts.pop(0)
                # print(parts)
                # print('\n#{}#'.format(parts))

                if parts:
                    d['Path']   = str(parts)
                    # print('\n#{}#'.format(parts))
                    # print(parts)
                    # pprint(d)

            
            z = {**d, **peer_data}

            output.append(z)
        return(output)
