from topo import *

def main():

    topo = Topology()
    topo.create(2,2,4)
    tg1=topo.attachTG('1-1')
    tg1=topo.attachTG('2-1')
    info = json.loads(topo.getAccessInfo())
    for k,v in info.items():
        print k,v     
    topo.linkImpair('1-1', ['1-2', '2-1'])
    import pdb; pdb.set_trace()
    topo.linkRepair('1-1', ['1-2', '2-1'])
    topo.cleanup()
    sys.exit()

    '''
    n1=topo.get_node('1-1')
    out = n1.exec_command(storage_create_file_cmd)
    out = n1.exec_command(storage_mdt_test_cmd)
    out = n1.exec_command(storage_nvmeof_cmd)
    out = tg1.exec_command(storage_fio_noverify)
    print out
    out = tg1.exec_command(storage_fio_noverify)
    print out
    import pdb; pdb.set_trace()
    '''
 
    topo.pauseRacks([3,4])
    topo.unpauseRacks([3,4])

    topo.pauseNodes(['1-2', '1-3', '2-2', '3-3', '4-4', '0-3', '0-20', '0-30'])
    topo.unpauseNodes(['1-2', '1-3', '2-2', '3-3', '4-4', '0-3', '0-20', '0-30'])

    topo.save()
    del topo
    topo = Topology()
    topo.load()

    tg1 = topo.attachTG('1-1')
    tg2 = topo.attachTG('2-2')
    tg3 = topo.attachTG('4-3')

    out = tg1.start_iperf(tg2)
    print out
    out = tg1.start_ab(tg3)
    print out

    topo.linkImpair('1-1', 'all spine links')
    topo.linkRepair('1-1', 'all spine links')
    topo.linkImpair('1-1', 'all inter-f1 links')
    topo.linkRepair('1-1', 'all inter-f1 links')
    topo.linkImpair('1-1', ['1-3', '0-2', '0-3'])
    topo.linkRepair('1-1', ['1-3', '0-2', '0-3'])

    topo.linkImpair('1-1', 'all spine links', 'loss', '10%', '25%')
    topo.linkRepair('1-1', 'all spine links')
    topo.linkImpair('1-1', 'all spine links', 'delay', '50ms', '10ms', 'normal')
    topo.linkRepair('1-1', 'all spine links')
    topo.linkImpair('1-1', 'all spine links', 'rate', '1mbit', '32kbit', '40ms')
    topo.linkRepair('1-1', 'all spine links')
    topo.linkImpair('1-1', 'all spine links', 'duplicate', '10%')
    topo.linkRepair('1-1', 'all spine links')
    topo.linkImpair('1-1', 'all spine links', 'corrupt', '10%')
    topo.linkRepair('1-1', 'all spine links')
    topo.linkImpair('1-1', 'all spine links', 'reorder', '10%', '50%', '10ms')
    topo.linkRepair('1-1', 'all spine links')


    topo.cleanup()

if __name__ == "__main__":
    main()
