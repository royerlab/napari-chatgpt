"""Aydin Classic denoising delegated code.

This module is injected at runtime by ``ImageDenoisingTool`` when the
LLM-generated code calls ``aydin_classic_denoising()``.  It wraps the
Aydin Classic class which provides filter-based denoising with multiple
variants (Butterworth, bilateral, wavelet, etc.).
"""

### SIGNATURE


def aydin_classic_denoising(image, batch_axes=None, chan_axes=None, variant=None):
    """Denoise an image using Aydin's Classic filter-based restoration algorithms.

    Parameters
    ----------
    image : numpy.ndarray
        Image to denoise
    batch_axes : array_like, optional
        Indices of batch axes. Batch dimensions/axes are dimensions/axes for which there is no-spatiotemporal correlation in the data. For example: different instance images stored in the same array.
    chan_axes : array_like, optional
        Indices of channel axes. This is the dimensions/axis of the numpy array that corresponds to the channel dimension of the image. Dimensions/axes that are not batch or channel dimensions are your standard X,Y,Z or T dimensions over which the data exhibits some spatiotemporal correlation.
    variant : str
        Algorithm variant. Can be: 'bilateral', 'butterworth', 'gaussian', 'gm', 'harmonic', 'nlm', 'pca', 'spectral', 'tv', 'wavelet'.

    Returns
    -------
    Denoised image : numpy.ndarray

    """

    # Turn on Aydin's logging:
    from aydin.util.log.log import Log

    Log.enable_output = True

    # Import Aydin:
    from aydin import Classic

    # Run and save the result
    classic = Classic(variant=variant)

    # Train
    classic.train(image, batch_axes=batch_axes, chan_axes=chan_axes)

    # Denoise
    denoised = classic.denoise(image, batch_axes=batch_axes, chan_axes=chan_axes)

    # Turn off Aydin's logging:
    Log.enable_output = False

    return denoised
