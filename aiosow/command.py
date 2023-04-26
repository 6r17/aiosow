#! env python3.11

import logging, asyncio, importlib, argparse, sys
from aiosow.setup import initialize
from aiosow.options import options
from aiosow.routines import spawn_routine_consumer


def load_composition(composition=None):
    debug = (
        "-d" in sys.argv
        or "--debug" in sys.argv
        or any(arg.find("-d") != -1 or arg.find("--debug") != -1 for arg in sys.argv)
    )
    if not "-h" in sys.argv:
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="[%(asctime)s][%(levelname)s] \t%(message)s",
            datefmt="%H:%M:%S",
        )
    parser = argparse.ArgumentParser()
    if not composition:
        parser.add_argument("composition", help="composition to run")
    parser.add_argument(
        "-c", "--config", help="Path to configuration file", default="", type=str
    )
    parser.add_argument(
        "-d", "--debug", default=False, action="store_true", help="Debug mode"
    )
    parser.add_argument(
        "-la",
        "--log_autofill",
        default=False,
        action="store_true",
        help="Log.debug every autofill arguments",
    )
    parser.add_argument(
        "--raise",
        default=False,
        action="store_true",
        help="Routines will raise errors and stop the execution",
    )
    try:
        if not composition:
            composition = sys.argv[1]
        composition = (
            f"{composition}.bindings" if not ".bindings" in composition else composition
        )
        importlib.import_module(composition)
    except Exception as e:
        logging.error("An error occured opening the composition")
        raise (e)
    for module_name in sys.modules.keys():
        if "bindings" in module_name and "aiosow" not in module_name:
            logging.info("+ composition %s", module_name)
    logging.info("--------------------------------")
    logging.info("-------------START--------------")
    logging.info("--------------------------------")
    for args, kwargs in options():
        parser.add_argument(*args, **kwargs)
    return vars(parser.parse_args())


def run(composition=None):
    memory = load_composition(composition=composition)
    logging.debug(memory)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = loop.run_until_complete(initialize(memory))
    logging.info("--------------------------------")
    logging.info("----------SETUP--DONE-----------")
    logging.info("--------------------------------")
    consumer = loop.run_until_complete(spawn_routine_consumer(memory))
    tasks = tasks + [consumer]
    # setups can return a task which is ran here
    # this allows setups to start tasks and still have them complete
    loop.run_until_complete(asyncio.gather(*tasks))
    if memory["run_forever"]:
        loop.run_forever()


if __name__ == "__main__":
    run()

__all__ = []
