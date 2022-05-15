# StandUp4NPR: Standardize SetUp for Empirically Comparison of Neural Program Repair Systems
___
## Experiment Results
>1. Evaluation_Results.zip: concrete evaluation results of every candidate predicted by the six NPR systems.  
|---Evaluation_Result   
&#8194;&#8194;&#8194;|---Diversity  
&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;|---Main    
&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;|---Bugs.jar      
&#8194;&#8194;&#8194;|---Empirical  
&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;|---Defects4J    
&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;|---Bears    
&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;|---QuixBugs      
&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;|---Manual_Check: manual check results of plausible/correct patches
___
## NPR4J-Benchmark
### Leaderboard (top-100 candidates)
| Diversity-Main <br> 12,815 bugs    | Bugs.jar <br> 480 bugs  | Defects4J <br> 260 bugs |Bears<br> 119 bugs |QuixBugs<br> 32 bugs |
| :----:| :----: | :----: | :----: | :----: |
| SequenceR / 2,900 | CoCoNut / 57 | SequenceR / 48 | CoCoNut / 19 |SequenceR / 15 |
| CoCoNut / 2,403 | SequenceR / 56 | CoCoNut / 48 |SequenceR / 16 |CoCoNut / 13 |
| Recoder /1,538 | Tufano / 43 | Recoder / 46 |Tufano / 9|Recoder / 10 |
| Tufano / 1,080 | Recoder / 34 | Tufano / 25 |Recoder / 5 |Tufano / 7|
| Edits / 179 | Edits / 20 | Edits / 15 |Edits 2 |Edits 6 |
| CODIT / 96 | CODIT / 8 | CODIT / 5 |CODIT 1 |CODIT 1 |

### Raw Data
>Raw data can be downloaded from this url (currently not available because this anonymous repository can not afford a too-large file):   
Structure of the raw data:  
|---Raw_Data   
&#8194;&#8194;&#8194;|---Evaluation  
&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;|---Diversity_Main  (12815 samples)  
&#8194;&#8194;&#8194;&#8194;&#8194;&#8194;|---Benchmarks   (Bugs.jar,Defects4J,QuixBugs,Bears)  
&#8194;&#8194;&#8194;|---Train  (144641 samples)  
&#8194;&#8194;&#8194;|---Valid  (13739 samples)   
&#8194;&#8194;&#8194;|---commit.json : commit message of each data sample  
Each sub dir contains seven types of data for each sample :   
>(1)buggy line (2)fix line (3)buggy method (4)fix method (5)buggy class (6)fix class (7)metas
 
We will also provide well-formed data stored in mongodb like following:
<img alt="one sample stored in the database" src="./images/mongodb_sample.PNG"/>
___
## NPR4J-Framework
### Data Preprocess
We are preparing a detailed documentation......   
Code Abstract: see directory "CodeAbstract", including:
>generating abstract codes for Tufano's system  
>generating classcontents for Recoder  
>generating abstract buggy context for SequenceR  
>......

Preprocess: see files "Dataset/Preprocess.py, Dataset/Preprocess_RawData.py" and "Dataset/PrepareData.py"  
### Training
To train a NPR system, you can use a simple command like this:
>python train.py -model NPR_SYSTEM_NAME -config CONFIG_FILE_PATH  

We are preparing a detailed documentation for how to write config files to train each model.  
Currently, for a reference, the directory "Config" contains some examples
### Generating Patches
To use a trained NPR system to generate patches, you can use a simple command like this:
>python translate.py -model NPR_SYSTEM_NAME -config CONFIG_FILE_PATH  
  
We are preparing a detailed documentation for how to write config files to use trained model.  
Currently, for a reference, the directory "Config" contains some examples
### Evaluating patches
Check if a patch is identical to the human-written patch: see "Evaluation.py"  
Run candidates on Defects4J, Bears and QuixBugs: still preparing, see Run_bears.py and Run_quixbugs.py for temporary reference
### Resources of trained NPR systems
We will release the six NPR models we trained for public usage  
currently not available because this anonymous repository can not afford a too-large file
### GPU memory requirements for each NPR model (with tuned hyperparameters in our experiment)
SequenceR: 20GB for training, less than 10GB for predicting  
Recoder: 40GB for training, 20GB for predicting  
CODIT:  less than 10GB for training and predicting  
Edits: less than 10GB for training and predicting  
CoCoNut (singleton mode): less than 10GB for training and predicting  
Tufano: less than 10GB for trainging and predicting  
