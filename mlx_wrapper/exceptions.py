class MLXError(Exception):
    """Base MLX wrapper exception."""


class NativeCallError(MLXError):
    """Raised when a native C function call fails."""


class DestroyedResourceError(MLXError):
    """Raised when a resource has been used after destruction."""


class ImageAllocationError(NativeCallError):
    """Inticates that mlx_new_image failed to create a new image."""


class ImageLoadError(NativeCallError):
    """Indicates a failure while loading an image."""


class FontLoadError(MLXError):
    """Indicates a failure while loading an TTF font."""


class AssetError(MLXError):
    """Base exception for all asset errors."""


class AssetManagerError(MLXError):
    """Base exception for all asset management errors."""


class RenderingError(AssetError):
    """Raised when a drawing operation fails."""
