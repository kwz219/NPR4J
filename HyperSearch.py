import logging

import clearml
from clearml import Task,task
from clearml.automation import HyperParameterOptimizer, UniformIntegerParameterRange, DiscreteParameterRange, \
    RandomSearch, UniformParameterRange


def job_complete_callback(
    job_id,                 # type: str
    objective_value,        # type: float
    objective_iteration,    # type: int
    job_parameters,         # type: dict
    top_performance_job_id  # type: str
):
    print('Job completed!', job_id, objective_value, objective_iteration, job_parameters)
    if job_id == top_performance_job_id:
        print('WOOT WOOT we broke the record! Objective reached {}'.format(objective_value))
def search_SR():
    try:
        from clearml.automation.optuna import OptimizerOptuna  # noqa
        aSearchStrategy = OptimizerOptuna
    except ImportError as ex:
        try:
            from clearml.automation.hpbandster import OptimizerBOHB  # noqa
            aSearchStrategy = OptimizerBOHB
        except ImportError as ex:
            logging.getLogger().warning(
                'Apologies, it seems you do not have \'optuna\' or \'hpbandster\' installed, '
                'we will be using RandomSearch strategy instead')
            aSearchStrategy = RandomSearch
    task = Task.init(
        project_name='Hyper-Parameter Optimization',
        task_name='Automatic Hyper-Parameter Optimization',
        task_type=Task.TaskTypes.optimizer,
        reuse_last_task_id=False
    )
    args = {
        'template_task_id': None,
        'run_as_service': False,
    }
    if not args['template_task_id']:
        args['template_task_id'] = Task.get_task(
            project_name='train', task_name='221_SR_origin').id
    optimizer=HyperParameterOptimizer(
        base_task_id=args['template_task_id'],
        hyper_parameters=[
        UniformIntegerParameterRange('Args/word_vec_size', min_value=128, max_value=512, step_size=128),
        UniformParameterRange('Args/learning_rate', min_value=0.0, max_value=1.0, step_size=0.05),
        DiscreteParameterRange('Args/batch_size', values=[8, 16, 32]),
        ],
        objective_metric_title='Valid',
        objective_metric_series='accuracy',
        objective_metric_sign='max',
        max_number_of_concurrent_tasks=2,
        optimizer_class=aSearchStrategy,
        execution_queue='default',
        pool_period_min=0.1,
        total_max_jobs=10,
        min_iteration_per_job=500,
        max_iteration_per_job=2000
    )
    # report every 12 seconds, this is way too often, but we are testing here J
    optimizer.set_report_period(0.5)
    # start the optimization process, callback function to be called every time an experiment is completed
    # this function returns immediately
    optimizer.start(job_complete_callback=job_complete_callback)
    top_exp=optimizer.get_top_experiments(top_k=3)
    print([t.id for t in top_exp])
    optimizer.stop()
    # set the time limit for the optimization process (2 hours)
search_SR()