import httplib
import json
import networkx as nx
import itertools
import time

class StaticFlowPusher(object):

    def __init__(self, server):
        self.server = server

    def get(self,url):
        ret = self.rest_call({}, 'GET',url)
        return json.loads(ret[2])

    
    def set(self, data, url):
        ret = self.rest_call(data, 'POST',url)
        return ret[0] == 200

    def remove(self, objtype, data, url):
        ret = self.rest_call(data, 'DELETE')
        return ret[0] == 200

    def rest_call(self, data, action, url):
        #path = '/wm/staticflowentrypusher/json'
        #path = '/wm/device/'
        path = url
        
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
            }
        body = json.dumps(data)
        conn = httplib.HTTPConnection(self.server, 8080)
        conn.request(action, path, body, headers)
        response = conn.getresponse()
        ret = (response.status, response.reason, response.read())
        #print ret
        conn.close()
        return ret


class Topology():
    
    def get_topology(self):
        #connect to the controller
        topo = StaticFlowPusher('127.0.0.1')

        #get links info
        test = topo.get('/wm/topology/links/json')
        
        print '\n Retrieve Link Information Completed \n'
        print test
        print '\n ----------------------------------- \n'
        
        return test

    def get_host(self):
        #connect to the controller
        topo = StaticFlowPusher('127.0.0.1')

        #get attachments
        host = topo.get('/wm/device/')
        print '\n Retrieve Access Node Information Completed \n'
        print host
        print '\n ------------------------------------------ \n'
        return host

    def multi_spaths(self,test,host):
        #add switch to the list
        i=0
        break_loop = 0
        switch = []
        while i < len(test):
            j=0
            if len(switch) == 0:
                switch.append(test[i]['dst-switch'])
            else:
                while j < len(switch):
                    if test[i]['dst-switch'] == switch[j]:
                        break_loop+=1
                        break            
                    j+=1
                if break_loop == 0:
                    switch.append(test[i]['dst-switch'])
                j=0
                break_loop = 0
                while j < len(switch):
                    if test[i]['src-switch'] == switch[j]:
                        break_loop+=1
                        break            
                    j+=1
                if break_loop == 0:
                    switch.append(test[i]['src-switch'])
                break_loop = 0
            i+=1

        #Create Graph
        G = nx.Graph()
        G.add_nodes_from(switch)
        print '\n Add Nodes Completed \n'
        print G.nodes()
        print '\n ------------------- \n'

        #Add links
        link_list = []
        i=0
        while i < len(test):
            link_list.append((test[i]['src-switch'],test[i]['dst-switch']))
            i+=1
        G.add_edges_from(link_list)
        print '\n Add Links Completed \n'
        print G.edges()
        print '\n ------------------- \n'

        #Add connected ports between switches
        link_port = []
        i=0
        while i < len(link_list):
            if (test[i]['src-switch'] == link_list[i][0]) & (test[i]['dst-switch'] == link_list[i][1]):
                link_port.append((test[i]['src-switch'],test[i]['src-port'],test[i]['dst-port'],test[i]['dst-switch']))
            i+=1
        print '\n Add Connected Ports Completed \n'
        print link_port
        print '\n ----------------------------- \n'
        
        #check access nodes
        source = []
        host_mac = []
        i=0
        j=0
        k=0
        while i < len(host):
            if host[i]['attachmentPoint'] != []:
                #find host mac
                host_mac.append({'mac':host[i]['mac'],'SW':host[i]['attachmentPoint'][0]['switchDPID'],'port':host[i]['attachmentPoint'][0]['port']})
                while j < len(source):
                    if source[j] == host[i]['attachmentPoint'][0]['switchDPID']:
                        k+=1
                        break
                    j+=1
                if k == 0:
                    source.append(host[i]['attachmentPoint'][0]['switchDPID'])
            k=0
            j=0
            i+=1    
        print '\n Check Access Nodes Completed \n'
        print source
        print '\n ---------------------------- \n'

        print '\n Hosts & Switches Completed \n'
        print host_mac
        print '\n ---------------------------- \n'
        
        #find unique pair of sources and destinations of access switches
        comb = [list(p) for p in itertools.combinations(source,2)]
        print '\n Unique Pairs of Sources and Destinations of Access Switches \n'
        print comb
        print '\n ----------------------------------------------------------- \n'

        #find pair of sources and destinations of hosts
        pair = []
        i=0
        j=0
        k=0
        src_host = []
        dest_host = []
        while i < len(comb):
            src_sw = comb[i][0]
            dest_sw = comb[i][1]
            while j < len(host_mac):
                if host_mac[j]['SW'] == src_sw:
                    src_host.append(host_mac[j]['mac'])
                j+=1
            j=0
            while j < len(host_mac):
                if host_mac[j]['SW'] == dest_sw:
                    dest_host.append(host_mac[j]['mac'])
                j+=1
            j=0
            i+=1
        
        while k<len(dest_host):
            pair.append({'src':src_host[k],'dest':dest_host[k]})
            k+=1
            
        print '\n Unique Pairs of Sources and Destinations of Hosts \n'
        print pair
        print '\n ------------------------------------------------- \n'

        #Find All Shortest paths
        i=0
        j=0
        k=0
        paths = []
        while i < len(comb):
            [paths.append(p) for p in nx.all_shortest_paths(G,comb[i][0],comb[i][1])]
            i+=1
        print '\n Find All Shortest Paths Completed \n'
        print paths
        print '\n --------------------------------- \n'
        return paths

        #Add flows
##        i=0
##        flow = []
##        while i<len(pair):
##            src_mac = pair[i]['src']
##            dst_mac = pair[i]['dest']
##            j=0
##            while j<len(host_mac):
##                if src_mac == host_mac[j]['mac']:
##                    src_switchDPID = host_mac[j]['SW']
##                if dst_mac == host_mac[j]['mac']:
##                    switchDPID = host_mac[j]['SW']
##                    output_port = host_mac[j]['port']
##                    output ="output=" + str(output_port)
##                    k=0
##                    chk_repeat=[]
##                    while k<len(paths):
##                        
##                        chk = 0
##                        if len(chk_repeat) != 0:
##                            
##                            n=0
##                            while n < len(chk_repeat):
##                                if k == chk_repeat[n]:
##                                    chk = 1
##                                n+=1
##                        else:
##                            
##                            if (switchDPID == paths[k][len(paths[k])-1]) & (src_switchDPID == paths[k][0]) & (chk == 0):
##                                chk_repeat.append(k)
##                                m = len(paths[k])-1
##                                while m > 0:
##                                    core = paths[k][m]
##                                    next_hop = paths[k][m-1]
##                                    l = 0
##                                    while l < len(link_port):
##                                        if (link_port[l][3] == core) & (link_port[l][0] == next_hop):
##                                            core_output_port = link_port[l][2]
##                                            core_output = "output=" + str(core_output_port)
##                                            core_flow_name = "core" + str(m)
##                                            flow.append({'switch': core,
##                                                 'name': core_flow_name,
##                                                 'src-mac': dst_mac,
##                                                 'dst-mac': src_mac,
##                                                 'actions': core_output})
##                                        l+=1
##                                    m-=1
##                        k+=1
##                    
##                j+=1    
##            flow_name = "test" + str(i)
##            flow.append({'switch': switchDPID,
##                                 'name': flow_name,
##                                 'src-mac': src_mac,
##                                 'dst-mac': dst_mac,
##                                 'actions': output})
##            i+=1
##        print flow
        #StaticFlowPusher.set(flow, '/wm/staticflowentrypusher/json')
##        static_forward = []
##        static_forward.append(['00:00:00:00:00:05','00:00:00:00:00:03',[3,3,1]])
##        static_forward.append(['00:00:00:00:00:06','00:00:00:00:00:04',[4,2,2]])
##        static_forward.append(['00:00:00:00:00:05','00:00:00:00:00:01',[3,2,1]])
##        static_forward.append(['00:00:00:00:00:06','00:00:00:00:00:02',[4,2,2]])          
##        static_forward.append(['00:00:00:00:00:01','00:00:00:00:00:03',[3,3,1]])
##        static_forward.append(['00:00:00:00:00:02','00:00:00:00:00:04',[4,3,2]])
##        
##        static_forward.append(['00:00:00:00:00:03','00:00:00:00:00:05',[3,4,1]])
##        static_forward.append(['00:00:00:00:00:04','00:00:00:00:00:06',[4,4,2]])
##        static_forward.append(['00:00:00:00:00:01','00:00:00:00:00:05',[3,4,1]])
##        static_forward.append(['00:00:00:00:00:02','00:00:00:00:00:06',[4,4,2]])
##        static_forward.append(['00:00:00:00:00:03','00:00:00:00:00:01',[3,2,1]])
##        static_forward.append(['00:00:00:00:00:04','00:00:00:00:00:02',[4,2,2]])
##
##        flow = []
##        i=0
##        count = 0
##        while i<6:
##            j=0
##            while j<3:
##                flow.append({'switch': paths[i][j],
##                      'name': 'flow' + str(count),
##                      'src-mac': static_forward[i][0],
##                      'dst-mac': static_forward[i][1],
##                      'actions': "output=" + str(static_forward[i][2][j])})
##                count+=1
##                j+=1    
##            i+=1

##        while i<12:
##            j=0
##            l=0
##            k=2
##            while j<3:
##                flow.append({'switch': paths[l][k],
##                      'name': 'flow' + str(count),
##                      'src-mac': static_forward[i][0],
##                      'dst-mac': static_forward[i][1],
##                      'actions': "output=" + str(static_forward[i][2][j])})
##                count+=1
##                k-=1
##                j+=1
##            l+=1
##            i+=1
    
    def add_flow1(self):
        ##add flows 1
        ##sw1
        topo_flow = StaticFlowPusher('127.0.0.1')
        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 1',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 2',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 3',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')
        
        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 4',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        
        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 5',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')
        
        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 6',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        ##sw2
        flow = {'switch': '00:00:00:00:00:00:00:02',
                'name': 'flow 7',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:02',
                'name': 'flow 8',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:02',
                'name': 'flow 9',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:02',
                'name': 'flow 10',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:02',
                'name': 'flow 11',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:02',
                'name': 'flow 12',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        ## sw3

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 13',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 14',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 15',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 16',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 17',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 18',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 19',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 20',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        ## sw4
        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 21',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 22',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 23',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 24',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 25',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 26',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 27',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 28',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

         ## sw5
        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 29',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 30',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 31',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 32',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 33',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 34',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 35',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 36',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        return 'ok'

    def add_flow2(self):
        topo_flow = StaticFlowPusher('127.0.0.1')
        ##add flows 2
        ##sw1
        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 1',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 2',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 3',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')
        
        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 4',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        
        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 5',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')
        
        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 6',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        ##sw2 -> sw1
        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 7',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 8',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 9',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 10',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=4"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 11',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:01',
                'name': 'flow 12',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')
        
        ## sw3

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 13',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 14',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 15',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 16',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 17',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 18',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 19',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:03',
                'name': 'flow 20',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        ## sw4
        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 21',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 22',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 23',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 24',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 25',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 26',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 27',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:04',
                'name': 'flow 28',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

         ## sw5
        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 29',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:01',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 30',
                'src-mac': '00:00:00:00:00:05',
                'dst-mac': '00:00:00:00:00:03',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 31',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:02',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 32',
                'src-mac': '00:00:00:00:00:06',
                'dst-mac': '00:00:00:00:00:04',
                'actions': "output=3"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 33',
                'src-mac': '00:00:00:00:00:01',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 34',
                'src-mac': '00:00:00:00:00:03',
                'dst-mac': '00:00:00:00:00:05',
                'actions': "output=1"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 35',
                'src-mac': '00:00:00:00:00:02',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')

        flow = {'switch': '00:00:00:00:00:00:00:05',
                'name': 'flow 36',
                'src-mac': '00:00:00:00:00:04',
                'dst-mac': '00:00:00:00:00:06',
                'actions': "output=2"}
        topo_flow.set(flow, '/wm/staticflowentrypusher/json')
        return 'ok'

    #get bytecount
    def get_count1(self,DPID):
        #connect to the controller
        topo = StaticFlowPusher('127.0.0.1')
        
        #get attachments
        counter = topo.get('/wm/core/switch/'+DPID+'/flow/json')
        ByteCount = []
        i=0
        #ByteCount = counter[DPID][0]['byteCount']
        #ByteCount = counter[DPID][0]['match']['dataLayerDestination']
        while i < 6:
            if (counter[DPID][i]['match']['dataLayerDestination'] == '00:00:00:00:00:04') & (counter[DPID][i]['match']['dataLayerSource'] == '00:00:00:00:00:06'):
                ByteCount.append({'src':'00:00:00:00:00:06','dst':'00:00:00:00:00:04','byte':counter[DPID][i]['byteCount']})
                
            if (counter[DPID][i]['match']['dataLayerDestination'] == '00:00:00:00:00:06') & (counter[DPID][i]['match']['dataLayerSource'] == '00:00:00:00:00:04'):
                ByteCount.append({'src':'00:00:00:00:00:04','dst':'00:00:00:00:00:06','byte':counter[DPID][i]['byteCount']})
                
            if (counter[DPID][i]['match']['dataLayerDestination'] == '00:00:00:00:00:02') & (counter[DPID][i]['match']['dataLayerSource'] == '00:00:00:00:00:06'):
                ByteCount.append({'src':'00:00:00:00:00:06','dst':'00:00:00:00:00:06','byte':counter[DPID][i]['byteCount']})
                
            if (counter[DPID][i]['match']['dataLayerDestination'] == '00:00:00:00:00:06') & (counter[DPID][i]['match']['dataLayerSource'] == '00:00:00:00:00:02'):
                ByteCount.append({'src':'00:00:00:00:00:02','dst':'00:00:00:00:00:06','byte':counter[DPID][i]['byteCount']})
                
            if (counter[DPID][i]['match']['dataLayerDestination'] == '00:00:00:00:00:02') & (counter[DPID][i]['match']['dataLayerSource'] == '00:00:00:00:00:04'):
                ByteCount.append({'src':'00:00:00:00:00:04','dst':'00:00:00:00:00:02','byte':counter[DPID][i]['byteCount']})
                
            if (counter[DPID][i]['match']['dataLayerDestination'] == '00:00:00:00:00:04') & (counter[DPID][i]['match']['dataLayerSource'] == '00:00:00:00:00:02'):
                ByteCount.append({'src':'00:00:00:00:00:02','dst':'00:00:00:00:00:04','byte':counter[DPID][i]['byteCount']})
            i+=1
        print '\n Retrieve ByteCount Information Completed \n'
        print ByteCount
        print '\n ---------------------------------------- \n'
        return ByteCount

    #save to file
    def save_file(self,paths):
        f = open('pathcaching.txt', 'w')
        i=0
        j=0
        str1 = ''
        int_temp = 0
        str2 = ''
        str_temp = ''
        while i < len(paths):
            while j < len(paths[i]):
                str_temp = paths[i][j]
                str_temp = str_temp.replace(':','')
                int_temp = int(str_temp,16)
                str2 = str2 + str(int_temp) + ' '
                j+=1
            str2 = str2 + '-1\n'
            j=0 
            i+=1
        f.write(str2)
        print '\n Writing File Completed \n'
        f.close



a = Topology()
var = a.get_topology()
var2 = a.get_host()
paths = a.multi_spaths(var,var2)
a.save_file(paths)
a.add_flow1()
i=0
temp = 0
while i<20:
    sum_count = 0
    BC = a.get_count1('00:00:00:00:00:00:00:02')
    j=0
    while j<6:
        sum_count = BC[j]['byte'] + sum_count
        j+=1
    if i != 0:
        if sum_count < (temp + 500):
            a.add_flow2()
            print "--------Change Path---------"
            i=20
    temp = sum_count
    time.sleep(10)
    i+=1












