# This code automatically prepares ligands, receptors and makes config files for autodock_vina calculations

import os

def prepare_ligand(infile,outfile):
    COMMAND = 'prepare_ligand4.py -l {0} -o {1} -A hydrogens 1> ./ligand_preparation_warnings.log'.format(infile,outfile)
    return os.system(COMMAND)

def prepare_receptor(infile,outfile):
    COMMAND = 'prepare_receptor4.py -r {0} -o {1} 1> ./receptor_preparation_warnings.log'.format(infile,outfile)
    return os.system(COMMAND)

def gather_inputs(receptor_dir,ligand_dir):
    if receptor_dir[-1]=='/':
        receptor_dir = receptor_dir[:-1]
    if ligand_dir[-1]=='/':
        ligand_dir = ligand_dir[:-1]
    receptors = [os.path.abspath(receptor_dir) + '/' + pdb for pdb in os.listdir(receptor_dir) \
                 if pdb.endswith('.pdb') or pdb.endswith('.mol2')]
    print('Found {0} receptors in {1}'.format(len(receptors),receptor_dir))
    ligands = [os.path.abspath(ligand_dir) + '/' + pdb for pdb in os.listdir(ligand_dir) \
              if pdb.endswith('.pdb') or pdb.endswith('.mol2')]
    print('Found {0} ligands in {1}'.format(len(ligands),ligand_dir))
    return receptors,ligands
    
def verify_outputs(receptors,ligands):
    # to verify if .pdbqt files are generated for all inputs
    count_lig = 0
    count_rec = 0
    
    flig = open('ligands_failed.log','w')
    frec = open('receptors_failed.log','w')
    for lig,rec in zip(ligands,receptors):
        # try ls -> will return non zero status if file absent
        status_lig = os.system('ls {0}qt > /dev/null'.format(lig))
        #print('ls {0}qt'.format(lig))
        #print(status_lig)
        status_rec = os.system('ls {0}qt > /dev/null'.format(rec))
        if status_lig==0: 
            count_lig+=1
        else:
            flig.write(lig)
        if status_rec==0: 
            count_rec+=1
        else:
            flig.write(rec)
    failed_lig_count = len(ligands)-count_lig
    failed_rec_count = len(receptors)-count_rec
    
    if failed_rec_count!=0:
        print('WARNING: {0} receptors not prepared!! See receptors_failed.log!'.format(failed_rec_count))
        flig.close()
    else:
        print('SUCCESS: All receptors prepared!')
        os.system('rm receptors_failed.log')
    
    if failed_lig_count!=0:
        print('WARNING: {0} ligands not prepared!! See ligands_failed.log!'.format(failed_lig_count))
        flig.close()
    else:
        print('SUCCESS: All ligands prepared!')
        os.system('rm ligands_failed.log')

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
        if not line.strip():
            # Nothing in line skip it
            continue
        else:
            items = line.strip().split(',')
            if len(items) != 9:
                #print(len(items))
                print('Something wrong in mapping_file ',)
                print('in line',)
                print(line)
                break
            else:
                config = 'config_{0}.txt'.format(int(items[0]))
                configs.append(config)
                config_f = open(config,'w')
                config_f.write(
'''receptor = {0}qt
ligand = {1}qt

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
    
    print('SUCCESS: Wrote {0} config txt files'.format(len(configs)))
    return configs

def make_jobs(vina_bin,configs,results_dir,submit=False):
    os.system('mkdir {0}'.format(results_dir))
    submitted = 0
    wrote = 0
    for config in configs:
        num = int(config.split('_')[-1][:-4])
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
        wrote+=1
        if submit: 
            submitted+=1
            os.system('qsub {0}'.format(jobname))
    
    print('SUCCESS: Wrote {0} job sh files'.format(len(configs)))
    if submit: print('SUCCESS: Submitted {0} job sh files'.format(len(configs)))
    return None
    
def main(map_file,rec_dir,lig_dir,results_dir,vina_bin,submit):
    receptors, ligands = gather_inputs(rec_dir,lig_dir)
    for rec in receptors:
        prepare_receptor(rec,'{0}.pdbqt'.format(rec[:-4]))
    for lig in ligands:
        prepare_ligand(lig,'{0}.pdbqt'.format(lig[:-4]))
        
    verify_outputs(receptors, ligands)
    configs = make_config(map_file)
    make_jobs(vina_bin,configs,results_dir,submit)
       
if __name__ == '__main__':  
    
    VINA_BIN = '/gpfs/group/cdm8/default/protein_external/autodock_vina/vina'
    
    MAP_FILE = raw_input('Enter map file name:')
    REC_DIR = raw_input('Enter receptor directory:')
    LIG_DIR = raw_input('Enter ligand directory:')
    
    RESULTS_DIR = raw_input('Enter a name for results directory:')
    SUBMIT = bool(int(raw_input('Auto submit? Answer as 1 or 0:')))
    
    main(MAP_FILE,REC_DIR,LIG_DIR,RESULTS_DIR,VINA_BIN,SUBMIT)
    
