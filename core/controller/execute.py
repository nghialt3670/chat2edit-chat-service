import ast
import inspect
import re
import textwrap
import traceback
from typing import Any, Coroutine, Dict, Iterable

from core.providers import ExecSignal, Provider
from db.models import ExecMessage

WRAPPER_FUNCTION_TEMPLATE = """
async def __wrapper_func(__context):
{command}
    
    for k, v in locals().items():
        if k != "__context":
            __context[k] = v
"""


async def execute(
    commands: Iterable[str],
    context: Dict[str, Any],
    provider: Provider,
) -> ExecMessage:
    signal = None
    executed_commands = []
    provider.set_context(context)

    for command in commands:
        executed_commands.append(command)
        command = preprocess_command(command, context)

        try:
            wrapper_func = create_wrapper_function(WRAPPER_FUNCTION_TEMPLATE, command)
            await wrapper_func(context)

        except Exception as e:
            print(traceback.format_exc())
            signal = ExecSignal(status="error", text=str(e))
            break

        signal = provider.get_signal()
        provider.clear_signal()

        if signal and signal.status in {"warning", "error"}:
            break

    return ExecMessage(
        status=signal.status,
        commands=executed_commands,
        text=signal.text,
        varnames=signal.varnames,
        response=signal.response,
    )


def preprocess_command(command: str, context: Dict[str, Any], context_name: str = "__context") -> str:
    def replace_var(var):
        # If it is a defined coroutine function (already in context)
        if var in context and inspect.iscoroutinefunction(context[var]):
            return f"await {context_name}['{var}']"

        return f"{context_name}['{var}']"
      
    processed_command = command
    while True:
        # Re-parse the command to get fresh AST after each replacement
        node_iter = ast.walk(ast.parse(processed_command, mode="exec"))
        replacements = []

        for node in node_iter:
            if isinstance(node, ast.Name) and node.id != context_name:
                start, end = node.col_offset, node.end_col_offset
                replacements.append((start, end, replace_var(processed_command[start:end])))

        if not replacements:
            break

        # Apply replacements in reverse order to avoid messing up indices
        for start, end, replacement in sorted(replacements, reverse=True):
            processed_command = processed_command[:start] + replacement + processed_command[end:]

    return processed_command


def create_wrapper_function(
    template: str, command: str, func_name: str = "__wrapper_func"
) -> Coroutine:
    local_vars = {}
    exec(
        template.format(command=textwrap.indent(command, "    ")),
        globals(),
        local_vars,
    )
    return local_vars[func_name]
