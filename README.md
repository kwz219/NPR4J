# StandUp4NPR: Standardize SetUp for Empirically Comparison of Neural Program Repair Systems
___
## NPR4J-Framework
### Data Preprocess
preparing
### Training
preparing
### Generating Patches
preparing
### Resources of trained NPR systems
preparing
### GPU memory requirements for each NPR model
SequenceR: 20GB for training, less than 10GB for predicting  
Recoder: 40GB for training, 20GB for predicting  
CODIT:  less than 10GB for training and predicting  
Edits: less than 10GB for training and predicting  
CoCoNut (singleton mode): less than 10GB for training and predicting  
Tufano: less than 10GB for trainging and predicting  
___
## NPR4J-Benchmark
### Leaderboard
preparing
### Raw Data
>Raw data can be downloaded from this url (currently not available because this anonymous repository can not afford a too-large file (nearly 1.5GB after zipped)):   
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
