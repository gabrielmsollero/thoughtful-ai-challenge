import logging
from RPA.Robocorp.WorkItems import WorkItems
from robocorp.tasks import task

@task
def minimal_task():
    library = WorkItems()
    library.get_input_work_item()

    variables = library.get_work_item_variables()
    for variable, value in variables.items():
        logging.info("%s = %s", variable, value)
