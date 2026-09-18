class MLXError(Exception):
    pass


class NativeCallError(MLXError):
    pass


class DestroyedResourceError(MLXError):
    pass


class ImageAllocationError(NativeCallError):
    pass


class ImageLoadError(NativeCallError):
    pass


class FontLoadError(MLXError):
    pass


class AssetError(MLXError):
    pass


class RenderingError(AssetError):
    pass
