from numpy.linalg import norm
from . import *#Pot, cur_path, bkz, copy
PATH = ''

def path_handler(path:str=cur_path, prev_dir:int=1):
    dirs = path.split('/')
    data_path = ''
    for dir in dirs[1:-prev_dir]:
        data_path += '/' + dir
    return data_path


def fp_file(path:str = PATH):
    import time
    from fpylll import SVP as fp_svp
    with open(path, 'rb') as file:
        basis = pkl.load(file)
    print(f"Requested norm according GH: {basis['R']}\n")
    s1 = time.time()
    bkz_basis = bkz(basis['basis'], block_size=basis['n']//2)
    fp = fp_svp.shortest_vector(bkz_basis, pruning=None)
    duration1 = time.time() - s1
    print("FPYLLL: ", norm(fp), "\tTIME: ", duration1)
    return norm(fp)


def b_file(path:str):
    try:
        with open(path, 'rb') as file:
            basis = pkl.load(file)['lll_basis']
    except FileNotFoundError:
        print(f'\n--- COMPARISON FAILED---\n'
            f'File \'{path}\' not found!')
        return None
    l_basis = list(basis)
    l_basis.sort(key=lambda  lb: norm(lb))
    it = iter(l_basis)
    best = next(it)
    while norm(best) == 0:
        best = next(it)
    return norm(best)


def request(protocol: str, ip: str, port: str) -> str:
    return protocol + "://" + ip + ":" + port


def settings():
    protocol = "tcp"
    ip = "127.0.0.1"
    port_pots = ["8072", "8078"]
    requests = [request(protocol, ip, port) for port in port_pots]
    return requests


def preprocessing_norm():
    data_path = 'random'
    if '--manual-basis' in sys.argv:  # Manually initialization of basis
        data_path = set_options(True).strip()
    if data_path == 'random':
        data_path = path_handler(path=cur_path, prev_dir=1) + '/data/basis/random'
    elif data_path == 'test':
        return None
    _best = b_file(data_path)
    print(f'\n-Best pre-processing norm {_best}-')
    return _best

def save_data(pre_norm:float, fpylll_result:float, my_result:float):
    # TODO: Save at JSON
    pass

def main():
    pot = Pot(*settings())
    # manager_conn, workers_conn = connect(*settings())
    print('To open the pot press ENTER')
    input()
    print('I ve grap the input')
    # pot(manager_conn, workers_conn)
    result = pot.run()
    print(f"\t***The norm of the SVP is {result}.***")
    pre_norm = preprocessing_norm()
    # save_data()
    exit(0)

def set_options(manBasis:bool=False):
    import argparse
    parser = argparse.ArgumentParser(prog="pot",
                                     usage='%(prog)s [options] commands',
                                     description="This module collects the results of all workers.",
                                     epilog="Good Luck!")
    PATH = cur_path + '/src/data/basis/'
    parser.add_argument('-f', '--fpylll',
                        help=f"With usage of FPYLLL lib, estimates the SVP result of given FILE path. "\
                             f"You can use as FILE path, just the name of file, if this one locates "\
                             f"in directory {PATH[:-1]}",
                        action="store",
                        type=str,
                        dest="file",
                        default= PATH)
    parser.add_argument('-F',
                        help=f'With usage of FPYLLL lib, estimates the SVP result, using default ' \
                             f'path: {PATH+ "test"} .\n',
                        action="store_true",
                        dest="fpylll"
                        )
    parser.add_argument('--manual-basis',
                        help="Set Manually Basis. The default mode is random calculation of basis, "
                             "according with optional settings below (dimensions, bits "
                             "and blocksize). You can set a predefined basis, or set a "
                             "test basis just to verify that module works fine. To execute in "
                             "test mode just use the flag \'-B test\'.",
                        action="store",
                        type=str,
                        dest="basis",
                        default="random")
    if manBasis:
        return parser.parse_args().basis
    if parser.parse_args().fpylll:
        return PATH + 'test'
    elif len(parser.parse_args().file.split('/')) == 1:
        return PATH + parser.parse_args().file
    return parser.parse_args().file


def fpylll_mode():
    PATH = set_options(False)
    print('Note: This mode just used to compare the algorithm\'s results, '
          'with FPYLLL results of given basis.\n')
    try:
        fp_file(PATH)
    except FileNotFoundError:
        print(f'\t- The file not found!\n\nTIP: Set the default mode -F or confirm that \"{PATH}\" exists.')
    finally:
        exit(0)


if __name__=="__main__":
    main()
elif __name__== "Lattice_SVP.pot.__main__":
    if (len(sys.argv)>1): # Means that user has defined some Flags.
        fpylll_mode() # This mode executes the FPYLLL's algorithm.
    else:
        main()
