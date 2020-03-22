1. module load python/3.6.3-anaconda5.0.1
2. source activate /gpfs/group/cdm8/default/protein_external/autodock_conda/
3. Download autodock_pipeline.zip and uncompress it and cd into its root folder
4. Edit map.csv file according to needs. Do not change the first line of the file 
since it has HEADER information used for parsing in the code.
Set up a simple script to write this file if all the jobs have common receptor or
binding site. 
5. python prepare_autodock_vina.py

Answer all questions and then..

The output should be bunch of job_{}.sh files where {} will be the serial number
of job as specified in map.csv file.
Also, they are automatically submitted if answered as 1 to Auto-submit question.
