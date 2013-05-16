# Created by Hyperion Gray, LLC
# Released under the Apache 2.0 License

import os
cwdir = os.path.dirname(__file__)
import xml.etree.ElementTree as ET
import sys
sys.path.append(cwdir)

class ConfigO:

    def __init__(self):
        self.tree = ET.parse(os.path.join(cwdir, "punk_fuzz.cfg.xml"))

    def get_xss_strings(self):

        xss_strings_elt = self.tree.findall('modules/xss_config/xss_strings/xss_string')
        xss_string_list = [xss_string.text for xss_string in xss_strings_elt]

        return xss_string_list

    def get_sqli_strings(self):

        sqli_strings_elt = self.tree.findall('modules/sqli_config/sqli_strings/sqli_string')
        sqli_string_list = [sqli_string.text for sqli_string in sqli_strings_elt]

        return sqli_string_list

    def get_bsqli_strings(self):

        bsqli_strings_elt = self.tree.findall('modules/bsqli_config/bsqli_strings/bsqli_string')
        bsqli_string_list = [bsqli_string.text for bsqli_string in bsqli_strings_elt]

        return bsqli_string_list

    def get_proxies_dic(self):

        protocol = self.tree.find('network_configs/proxy').get('type')
        ip_col_port = self.tree.find('network_configs/proxy/ip_port').text

        #return nothing if ip and port are missing in config - i.e. don't use proxy
        if not ip_col_port or not protocol:
            return {}

        #need it in this silly format to pass to requests lib
        return {protocol:ip_col_port}

    def get_solr_urls(self):

        solr_summary_url = self.tree.find('network_configs/solr/summary_url').text
        solr_details_url = self.tree.find('network_configs/solr/detail_url').text

        return {'solr_summary_url':solr_summary_url, 'solr_details_url':solr_details_url}
        
    def get_pagesize_limit(self):
    
        pagesize_limit = self.tree.find('fuzz_configs/pagesize_limit').text        
        return int(pagesize_limit)

    def get_contentl_check(self):
    
        contentl_requirement = self.tree.find('fuzz_configs/contentl_check').text
        if "yes" in contentl_requirement:
            return True

        else:
            return False

    def get_content_type_check(self):
    
        content_type_requirement = self.tree.find('fuzz_configs/content_type_check').text    
        if "yes" in content_type_requirement:
            return True
            
        else:
            return False        

    def get_contentl_check_wfallback(self):

        content_type_fallback_requirement = self.tree.find('fuzz_configs/contentl_check_wfallback').text
        if "yes" in content_type_fallback_requirement:
            return True

        else:
            return False
    
    def get_allowed_content_types(self):

        find_allowed_content_types = self.tree.findall('fuzz_configs/allowed_content_types/type')
        allowed_content_types = []

        for type in find_allowed_content_types:

            allowed_content_types.append(type.text)

        return allowed_content_types
        
    def get_page_memory_load_limit(self):
    
        find_page_memory_load_limit = self.tree.findall('fuzz_configs/page_memory_load_limit')        

        return int(find_page_memory_load_limit[0].text)
    

if __name__ == "__main__":

    print ConfigO().get_xss_strings()
    print ConfigO().get_proxies_dic()
    print ConfigO().get_sqli_strings()
    print ConfigO().get_pagesize_limit()
#    print ConfigO().get_contentl_check()
#    print ConfigO().get_content_type_check()
    print ConfigO().get_contentl_check_wfallback()
    print ConfigO().get_allowed_content_types()
    print ConfigO().get_page_memory_load_limit()
