
from aiosow.bindings import setup, wire, make_async


@make_async
def get_input(*__args__, **__kwargs__) -> str:
    return input('< ')

def interpret(data: str) -> None:
    print(f'> {data}')

@setup
async def launch_shell():
    when, do = wire()
    when_complete_with, relaunch = wire()
    
    ask = when(get_input)
    when_complete_with(interpret)
    do(interpret)
    relaunch(ask)
    setup(ask)
