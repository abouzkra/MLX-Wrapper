from abc import ABC, abstractmethod
from typing import Any

from mlx_wrapper.exceptions import DestroyedResourceError


class Asset(ABC):
    """Base class for assets.

    Every asset in the MLX wrapper should inherit from it.
    It ensures that an asset can't be used after destroy() by clearing
    the subclass's writable attributes and setting a _destroyed state
    as True.

    """

    def destroy(self) -> None:
        """Destroy the asset, cleaning up its resources.

        It calls back the _custom_destroy method for customized destruction
        for each asset, clears the writable attributes and sets the
        _destroyed state as True.
        """
        if self.__dict__.get("_destroyed"):
            return
        self._custom_destroy()
        self.__dict__.clear()
        self.__dict__["_destroyed"] = True

    @abstractmethod
    def _custom_destroy(self) -> None:
        """Hook for customized asset destruction.

        This should be overridden in every subclass to provide comprehensive
        asset destruction.
        """
        pass

    def __getattr__(self, name: str) -> Any:
        """Intercepts missing attributes to prevent destroyed asset usage.

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
