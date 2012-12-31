#!/usr/bin/env python
import sys
import os
import datetime
from urlparse import urlparse
cwdir = os.path.dirname(__file__)
sys.path.append(os.path.join(cwdir, "../", "pysolr/"))
sys.path.append(os.path.join(cwdir, "../", "fuzzer_config/"))
import pysolr
import fuzz_config_parser

class PunkMapReduceIndexer:

    def __init__(self, domain, domain_vuln_list, del_current = True):

        configo = fuzz_config_parser.ConfigO()
        solr_urls_dic = configo.get_solr_urls()

        solr_summary_url = solr_urls_dic['solr_summary_url']
        solr_details_url = solr_urls_dic['solr_details_url']

        self.conn_summ = pysolr.Solr(solr_summary_url)
        self.conn_details = pysolr.Solr(solr_details_url)

        self.solr_summary_doc = self.conn_summ.search('id:' + '"' + domain + '"', rows=1)

        self.domain_vuln_list = domain_vuln_list
        self.domain = domain

        self.reversed_domain = self.__reverse_url(domain)

        if del_current:

            self.__clear_current()

    def __clear_current(self):
        '''Clear the solr details for the current domain. '''

        self.conn_details.delete(q = "url_main:" + self.reversed_domain)
        
    def __reverse_url(self, url):

        #strip the trailing slash from the url if it has one
        last_char = url[-1]
        if last_char == "/":

            url = url[:-1]
        
        #starting with http://www.google.com
        out = urlparse(url)

        #http or https is the first element
        protocol = out.scheme

        #www.google.com -> [www,google,com]
        url_list = out.netloc.split(".")

        #list becomes -> [com,google,www]
        url_list.reverse()

        #return com.google.www
        url_reversed = ".".join(url_list)

        return url_reversed

    def add_vuln_info(self):
        '''Index the vulnerabilities and details info'''

        vuln_details_dic_list = []        
        vuln_summary_dic = {}

        vuln_c = 0
        xss_c = 0
        sqli_c = 0
        bsqli_c = 0

        for vuln in self.domain_vuln_list:

            vuln_details_dic = {}
            vuln_c += 1
            #get details for solr_details
            
            protocol = vuln[4]
            url_main = self.reversed_domain
            v_url = vuln[0]
            bugtype = vuln[2]
            parameter = vuln[3]
            id = self.reversed_domain + "." + str(vuln_c)

            vuln_details_dic["protocol"] = protocol
            vuln_details_dic["url_main"] = url_main
            vuln_details_dic["v_url"] = v_url
            vuln_details_dic["bugtype"] = bugtype
            vuln_details_dic["parameter"] = parameter
            vuln_details_dic["id"] = id

            vuln_details_dic_list.append(vuln_details_dic)
            
            #get the count of vulnerabilities by type
            
            if vuln[2] == "xss":
                xss_c += 1

            if vuln[2] == "sqli":
                sqli_c += 1

            if vuln[2] == "bsqli":
                bsqli_c += 1

        #commit details vulnerabilities in batch
        print vuln_details_dic_list
        self.conn_details.add(vuln_details_dic_list)                

        #set the summary details dictionary and commit
        for summ_doc in self.solr_summary_doc:

            summ_doc["xss"] = xss_c
            summ_doc["sqli"] = sqli_c
            summ_doc["bsqli"] = bsqli_c
            
        self.conn_summ.add(self.solr_summary_doc)

if __name__ == "__main__":

    vuln_list = [["http://www.mysticboarding.com/dealers/distributors/?did=%22%3E%3CSCrIpT%3Ealert%28313371234%29%3C%2FScRiPt%3E", "\"><SCrIpT>alert(313371234)</ScRiPt>", "xss", "did", "http"], ["http://www.mysticboarding.com/dealers/distributors/?did=%22%3E%3C%2FTITLE%3E%3CSCRIPT%3Ealert%28313371234%29%3B%3C%2FSCRIPT%3E", "\"></TITLE><SCRIPT>alert(313371234);</SCRIPT>", "xss", "did", "http"], ["http://www.mysticboarding.com/dealers/distributors/?did=%22%3E%3CScR%3Cscript%3EiPt%3Ealert%28313371234%29%3C%2FSCr%3Cscript%3EIpT%3E", "\"><ScR<script>iPt>alert(313371234)</SCr<script>IpT>", "xss", "did", "http"]]
    domain = "http://www.mysticboarding.com/"

    PunkMapReduceIndexer(domain, vuln_list)
    
