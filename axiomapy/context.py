"""
Copyright © 2022 Qontigo GmbH.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""
import contextvars
import logging
from threading import local
from typing import Type, TypeVar

from axiomapy.axiomaexceptions import AxiomaUninitialisedError

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

T = TypeVar("T")


thread_local = local()

# Use context vars to behave correctly when running asynchronously when a thread can
# be shared across contexts
# however will roll back due to this:
# https://github.com/ipython/ipython/issues/11565
# which will mean session is not shared across cells with context var
current_session_var = contextvars.ContextVar("current_session_var", default=None)
context_stacks_var = contextvars.ContextVar("context_stacks", default={})
entered_var = contextvars.ContextVar("context_stacks", default={})


# use meta class to create a property on the type (not instance)
class BaseMeta(type):
    @property
    def current(cls: Type[T]) -> T:
        # current = current_session_var.get()
        current = getattr(thread_local, "_current", None)

        if current is None:
            raise AxiomaUninitialisedError(f"{cls.__name__} is not initialised")
        # _logger.info(f"Using current session '{current.name}'")
        return current

    # set current
    @current.setter
    def current(cls: Type[T], session: T):
        setattr(thread_local, "_current", session)
        # current_session_var.set(session)
        _logger.debug(f"Set session to {getattr(session, 'name', 'None' )}")


class BaseContext(metaclass=BaseMeta):
    """Manages context switch for session classes.

    Args:
        metaclass ([type], optional): [description]. Defaults to BaseMeta.
    """

    def _add_to_stack(self, name: str, clz):
        """Records the session before starting the new context

        Args:
            name (str): [description]
            current ([type]): [description]
        """
        # stacks = context_stacks_var.get()
        # stack = stacks.get(f"{name}_contextStack", [])

        stack = getattr(thread_local, f"{name}_contextStack", [])

        # wrap in try in case as accessing current that is none raises
        try:
            current = clz.current
            stack.append({"current": current, "entered": False})
            # store in thread local for now...
            setattr(thread_local, f"{name}_contextStack", stack)
            # is this needed?
            # stacks[f"{name}_contextStack"] = stack
            # context_stacks_var.set(stacks)
        except Exception:
            pass

        # entered = entered_var.get()
        # entered["{}_entered".format(name)] = True
        # entered_var.set(entered)
        # use thread local for now...
        setattr(thread_local, "{}_entered".format(name), True)

    def _pop_from_stack(self, name: str):
        """Closes and returns the previous session when leaving the context

        Args:
            name (str): [description]

        Returns:
            [type]: [description]
        """
        # stacks = context_stacks_var.get()
        # stack = stacks.get(f"{name}_contextStack", [])
        stack = getattr(thread_local, f"{name}_contextStack", [])
        previous_current = None
        previous_entered = False
        if len(stack) > 0:
            previous = stack.pop()
            previous_current = previous.get("current", None)
            previous_entered = previous.get("entered", False)
        entered = entered_var.get()
        entered["{}_entered".format(name)] = previous_entered
        entered_var.set(entered)
        # use thread local for now...
        setattr(thread_local, "{}_entered".format(name), previous_entered)

        return previous_current

    def __enter__(self):
        clz = self._cls
        self._add_to_stack(clz.__name__, clz)
        clz.current = self
        self._on_enter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._on_exit(exc_type, exc_val, exc_tb)
        finally:
            clz = self._cls
            clz.current = self._pop_from_stack(clz.__name__)

    async def __aenter__(self):
        clz = self._cls
        self._add_to_stack(clz.__name__, clz)
        clz.current = self
        await self._aon_enter()
        return self

    async def __aexit__(self, exc_type=None, exc_value=None, traceback=None,) -> None:
        try:
            await self._aon_exit(exc_type, exc_value, traceback)
        finally:
            clz = self._cls
            clz.current = self._pop_from_stack(clz.__name__)

    @property
    def _cls(self) -> BaseMeta:
        """Iterates through subclasses to get to the base 'context'
        to manage the associated session

        Returns:
            BaseMeta -- [description]
        """
        seen = set()
        stack = [self.__class__]
        cls = None

        while stack:
            base = stack.pop()
            if BaseContext in base.__bases__:
                cls = base
                break

            if base not in seen:
                seen.add(base)
                stack.extend(b for b in base.__bases__ if issubclass(b, BaseContext))

        return cls or self.__class__

    @property
    def is_entered(self) -> bool:
        # return entered_var.get("{}_entered".format(self._cls.__name__), False)
        return getattr(thread_local, "{}_entered".format(self._cls.__name__), False)

    def _on_enter(self):
        pass

    def _on_exit(self, exc_type, exc_val, exc_tb):
        pass

    async def _aon_enter(self):
        pass

    async def _aon_exit(self, exc_type, exc_val, exc_tb):
        pass
