#!/usr/bin/python
# -*- coding: utf-8 -*-



import fire
from subprocess import call
import re

port_query_reg_str = r"CSM\s+\[{}\].*client_src_port\s+(\d+),\s+csp_src_port\s+(\d+)"


class QueryCmd():
    def get_port(self,logcat_path,csm_id):
        print "get_port,csm_id=" + csm_id
        with open(logcat_path, "r") as ins:
            for line in ins:
                if csm_id not in line:
                    continue
                if "client_src_port" not in line and "csp_src_port" not in line:
                    continue
                #print line
                reg_str = port_query_reg_str.format(csm_id)
                matchObj = re.search(reg_str, line)
                if matchObj:
                    local_port = matchObj.group(1)
                    remote_port = matchObj.group(2)
                    print "query result for [{}]:tcp.port eq {} and tcp.port eq {}".format(csm_id,local_port,remote_port)
                    return

        pass


def main():
    fire.Fire(QueryCmd)
    pass


if __name__ == "__main__":
    main()