#! env python3.11

import logging, asyncio, importlib, argparse, sys
from aiosow.setup import initialize, should_trigger_routines
from aiosow.options import options, commands
from aiosow.routines import spawn_routine_consumer


def load_composition(composition=None, **kwargs):
    debug = (
        "-d" in sys.argv
        or "--debug" in sys.argv
        or any(
            arg.find("-d") != -1 or arg.find("--debug") != -1
            for arg in sys.argv
        )
    )
    if "--log" in sys.argv or kwargs.get("log", False):
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format="[%(asctime)s][%(levelname)s] \t%(message)s",
            datefmt="%H:%M:%S",
        )
    parser = argparse.ArgumentParser()

    if not composition:
        parser.add_argument("composition", help="composition to run")
    # parser.add_argument(
    #    "-c", "--config", help="Path to configuration file", default="", type=str
    # )
    parser.add_argument(
        "-d", "--debug", default=False, action="store_true", help="Debug mode"
    )
    parser.add_argument(
        "-la",
        "--log_autofill",
        default=False,
        action="store_true",
        help="Log.info autofilled functions",
    )
    parser.add_argument(
        "--raise",
        default=False,
        action="store_true",
        help="Routines will raise errors and stop the execution",
    )
    parser.add_argument(
        "--log", help="Displays logs", action="store_true", default=False
    )
    try:
        if not composition:
            composition = sys.argv[1]
        composition = (
            f"{composition}.bindings"
            if not ".bindings" in composition
            else composition
        )
        importlib.import_module(composition)
    except Exception as e:
        logging.error("An error occured opening the composition")
        raise (e)
    for module_name in sys.modules.keys():
        if "bindings" in module_name and "aiosow" not in module_name:
            logging.info("+ composition %s", module_name)
    for args, kwargs in options():
        parser.add_argument(*args, **kwargs)
    for name, function in commands():
        subparsers = parser.add_subparsers()
        newcmd_parser = subparsers.add_parser(name)
        newcmd_parser.set_defaults(
            func=function
        )  # set the default function to be called for this subcommand
    args = parser.parse_args()
    result = vars(args)
    if getattr(args, "func", None):
        args.func(args)
        result["run_forever"] = False
    return result


def run(composition=None, **kwargs):
    memory = load_composition(composition=composition, **kwargs)
    logging.debug(memory)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = loop.run_until_complete(initialize(memory))
    memory["running"] = True
    if should_trigger_routines():
        consumer = loop.run_until_complete(spawn_routine_consumer(memory))
        if consumer:
            tasks = tasks + [consumer]
    loop.run_until_complete(asyncio.gather(*tasks))
    if memory.get("run_forever", False):
        loop.run_forever()


if __name__ == "__main__":
    run()

__all__ = []
