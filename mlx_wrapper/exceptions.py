class MLXError(Exception):
    """Base MLX wrapper exception."""
    pass


class NativeCallError(MLXError):
    """Raised when a native C function call fails."""
    pass


class DestroyedResourceError(MLXError):
    """Raised when a resource has been used after destruction."""
    pass


class ImageAllocationError(NativeCallError):
    """Inticates that mlx_new_image failed to create a new image."""
    pass


class ImageLoadError(NativeCallError):
    """Indicates a failure while loading an image."""
    pass


class FontLoadError(MLXError):
    """Indicates a failure while loading an TTF font."""
    pass


class AssetError(MLXError):
    """Base exception for all asset errors."""
    pass


class AssetManagerError(MLXError):
    """Base exception for all asset management errors."""
    pass


class RenderingError(AssetError):
    """Raised when a drawing operation fails."""
    pass
