"""Base class implementation for assets."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from mlx import Mlx

from mlx_wrapper.exceptions import DestroyedResourceError, MLXError


class Asset(ABC):
    """Base class for assets.

    Every asset in the MLX wrapper should inherit from it.
    It ensures that an asset can't be used after destroy() by clearing
    the subclass's writable attributes and setting a _destroyed state
    as True.

    """

    __mlx: ClassVar[Mlx | None] = None
    __mlx_ptr: ClassVar[int | None] = None
    __win_ptr: ClassVar[int | None] = None

    @classmethod
    def set_context(
        cls, mlx: Mlx | None, mlx_ptr: int | None, win_ptr: int | None
    ) -> None:
        """Set the MLX context for the asset."""
        if (
            cls.__mlx is not None
            or cls.__mlx_ptr is not None
            or cls.__win_ptr is not None
        ):
            raise MLXError("MLX context is already set. Clear it first.")

        cls.__mlx = mlx
        cls.__mlx_ptr = mlx_ptr
        cls.__win_ptr = win_ptr

    @classmethod
    def get_context(cls) -> tuple[Mlx, int, int]:
        """Return the current MLX context, raising an error if not set."""
        if cls.__mlx is None or not cls.__mlx_ptr or not cls.__win_ptr:
            raise MLXError("Found no MLX context. Initialize an app first!")

        return cls.__mlx, cls.__mlx_ptr, cls.__win_ptr

    @classmethod
    def clear_context(cls) -> None:
        """Clear the MLX context, resetting the class-level variables."""
        cls.__mlx = None
        cls.__mlx_ptr = None
        cls.__win_ptr = None

    def destroy(self) -> None:
        """Destroy the asset, cleaning up its resources.

        It calls back the _custom_destroy method for customized destruction
        for each asset, clears the writable attributes and sets the
        _destroyed state as True.
        """
        if self.__dict__.get("_destroyed"):
            raise DestroyedResourceError(
                "Attemted to destroy already destroyed asset "
                f"{self.__class__.__name__}"
            )
        self._custom_destroy()
        self.__dict__.clear()
        self.__dict__["_destroyed"] = True

    @abstractmethod
    def _custom_destroy(self) -> None:
        """Customize asset destruction.

        This should be overridden in every subclass to provide comprehensive
        asset destruction.
        """

    def __getattr__(self, name: str) -> Any:
        """Intercept missing attributes to prevent destroyed asset usage.

        name (str): Name of the attribute.

        Raises:
            DestroyedResourceError: If a destroyed asset's attribute has been
                used.
        """
        if self.__dict__.get("_destroyed", False):
            raise DestroyedResourceError(
                f"Tried to access '{name}' on destroyed "
                f"{self.__class__.__name__}"
            )
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )
