from clearml import Task
task = Task.init(project_name='great project', task_name='best experiment')
config_file_yaml = task.connect_configuration(name="SequenceR yaml", configuration='D:\DDPR\Config\SequenceR_train.yaml', )