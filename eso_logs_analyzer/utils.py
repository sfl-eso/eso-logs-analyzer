from datetime import datetime


def tqdm(iterable=None, desc=None, total=None, leave=True, file=None,
         ncols=None, mininterval=0.1, maxinterval=10.0, miniters=None,
         ascii=None, disable=False, unit='it', unit_scale=False,
         dynamic_ncols=False, smoothing=0.3, bar_format=None, initial=0,
         position=None, postfix=None, unit_divisor=1000, write_bytes=False,
         lock_args=None, nrows=None, colour=None, delay=0, gui=False,
         **kwargs):
    """
    Wrapper for tqdm that uses the logging_redirect_tqdm functionality to allow logging with tqdm progress bars
    while maintaining the same tqdm api.
    See https://tqdm.github.io/docs/contrib.logging/
    """
    import tqdm as o_tqdm
    from tqdm.contrib.logging import logging_redirect_tqdm
    with logging_redirect_tqdm():
        for obj in o_tqdm.tqdm(iterable=iterable, desc=desc, total=total, leave=leave, file=file,
                               ncols=ncols, mininterval=mininterval, maxinterval=maxinterval, miniters=miniters,
                               ascii=ascii, disable=disable, unit=unit, unit_scale=unit_scale,
                               dynamic_ncols=dynamic_ncols, smoothing=smoothing, bar_format=bar_format, initial=initial,
                               position=position, postfix=postfix, unit_divisor=unit_divisor, write_bytes=write_bytes,
                               lock_args=lock_args, nrows=nrows, colour=colour, delay=delay, gui=gui,
                               **kwargs):
            yield obj


def parse_epoch_time(epoch_time: str) -> datetime:
    return datetime.fromtimestamp(int(epoch_time) / 1000)


def all_subclasses(cls):
    classes = []
    for subclass in cls.__subclasses__():
        if subclass.event_type is not None:
            classes.append(subclass)
        else:
            classes.extend(all_subclasses(subclass))
    return classes
