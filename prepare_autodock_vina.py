# This code automatically prepares ligands, receptors and makes config files for autodock_vina calculations

import os

def prepare_ligand(infile,outfile):
    print(infile)
    COMMAND = 'prepare_ligand4.py -l {0} -o {1} -v -A hydrogens'.format(infile,outfile)
    return os.system(COMMAND)

def prepare_receptor(infile,outfile):
    COMMAND = 'prepare_receptor4.py -r {0} -o {1} -v'.format(infile,outfile)
    return os.system(COMMAND)

def gather_inputs(receptor_dir,ligand_dir):
    receptors = [os.path.abspath(receptor_dir) + '/' + pdb for pdb in os.listdir(receptor_dir) \
                 if pdb.endswith('.pdb') or pdb.endswith('.mol2')]
#     print('Found {0} receptors in {1} .'.format(receptor_dir))
    ligands = [os.path.abspath(ligand_dir) + '/' + pdb for pdb in os.listdir(ligand_dir) \
              if pdb.endswith('.pdb') or pdb.endswith('.mol2')]
#     print('Found {0} ligands in {1} .'.format(receptor_dir))
    return receptors,ligands

def make_config(mapping_file):
    # mapping_file header line
    # NUM, RECEPTOR, LIGAND, xc, yc, zc, xs, ys, zs
    f = open(mapping_file)
    first = False
    configs = []
    for line in f:
        # make sure first line starts as header
        if not first:
            assert(line.startswith('NUM, RECEPTOR, LIGAND, xc, yc, zc, xs, ys, zs'))
            first = True
            continue
        items = line.strip().split(',')
        if len(items) != 9:
            print('Something wrong in mapping_file!')
            break
        config = 'config_{0}.txt'.format(int(items[0]))
        configs.append(config)
        config_f = open(config,'w')
        config_f.write(
'''receptor = {0}
ligand = {1}

center_x = {2}
center_y = {3}
center_z = {4}

size_x = {5}
size_y = {6}
size_z = {7}

exhaustiveness = 20
'''.format(*items[1:])
        )
        config_f.close()
        
    return configs

def make_jobs(vina_bin,configs,results_dir,submit=False):
    os.system('mkdir {0}'.format(results_dir))
    for config in configs:
        num = int(config.split('_')[-1].format('.txt')[0])
        os.system('mkdir {0}/{1}'.format(results_dir,num))
        job = '''
#PBS -l nodes=1:ppn=1

#PBS -l walltime=2:00:00

#PBS -l pmem=1gb

#PBS -l mem=1gb

#PBS -A cdm8_f_g_bc_default
#PBS -j oe

set -u

cd $PBS_O_WORKDIR

echo " "

echo " "

echo "JOB Started on $(hostname -s) at $(date)"

{0} --config config_{1}.txt --out {2}/{1}/out.pdbqt --log {2}/{1}/log
        '''.format(vina_bin,num,results_dir)
        jobname = 'job_{0}.sh'.format(num)
        f = open(jobname,'w')
        f.write(job)
        f.close()
        if submit: os.system('qsub {0}'.format(jobname))
    return None
    
def main(map_file,rec_dir,lig_dir,results_dir,vina_bin,submit):
    configs = make_config(map_file)
    receptors, ligands = gather_inputs(rec_dir,lig_dir)
    print(receptors,ligands)
    for rec in receptors:
        prepare_receptor(rec,'{}.pdbqt'.format(rec[:-4]))
    for lig in ligands:
        prepare_ligand(lig,'{}.pdbqt'.format(lig[:-4]))
    make_jobs(vina_bin,configs,results_dir,submit)
    
if __name__ == '__main__':  
    MAP_FILE = 'map.csv'
    REC_DIR = './rec'
    LIG_DIR = './lig'
    RESULTS_DIR = './results'
    VINA_BIN = '/gpfs/group/cdm8/default/protein_external/autodock_vina/vina'
    
    SUBMIT = bool(int(raw_input('Auto submit? Answer as 1 or 0:')))
    
    main(MAP_FILE,REC_DIR,LIG_DIR,RESULTS_DIR,VINA_BIN,SUBMIT)
