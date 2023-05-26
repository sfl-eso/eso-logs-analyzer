from functools import wraps


def requires_load(function):
    """
    This decorator checks if the data that is computed by the function has been loaded already.
    May only be used on methods of DataProcessor subclasses.
    :param function: the method that is called by the command
    :return: the wrapped function
    """

    @wraps(function)
    def check_is_loaded(*args, **kwargs):
        from processing import DataProcessor
        data_processor: DataProcessor = args[0]
        assert data_processor.is_loaded, "No data loaded yet!"
        return function(*args, **kwargs)

    return check_is_loaded


def requires_target(function):
    """
    This decorator checks if the target for which data is computed is part of the encounter that is being processed
    May only be used on methods of class Encounter or EncounterPlayer that have the target object as first parameter.
    :param function: the method that is called by the command
    :return: the wrapped function
    """

    @wraps(function)
    def check_target_is_in_encounter(*args, **kwargs):
        from processing import Encounter, EncounterPlayer
        from loading import UnitAdded
        encounter: Encounter = None
        if isinstance(args[0], EncounterPlayer):
            encounter = args[0].encounter
        elif isinstance(args[0], Encounter):
            encounter = args[0]
        else:
            raise ValueError(
                f"Annotated function is invalid on methods outside classes containing {Encounter.__name__}")
        target: UnitAdded = args[1]
        assert target in encounter.enemy_units, f"Target {target} is not part of encounter {encounter}"
        return function(*args, **kwargs)

    return check_target_is_in_encounter
