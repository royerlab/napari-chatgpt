### SIGNATURE
def aydin_fgr_denoising(image, batch_axes=None, chan_axes=None, variant=None):
    """Method to denoise an image with Aydin's Noise2Self FGR (Feature Generation and Regression) approach.

    Parameters
    ----------
    image : numpy.ndarray
        Image to denoise
    batch_axes : array_like, optional
        Indices of batch axes. Batch dimensions/axes are dimensions/axes for which there is no-spatiotemporal correlation in the data. For example: different instance images stored in the same array.
    chan_axes : array_like, optional
        Indices of channel axes. This is the dimensions/axis of the numpy array that corresponds to the channel dimension of the image. Dimensions/axes that are not batch or channel dimensions are your standard X,Y,Z or T dimensions over which the data exhibits some spatiotemporal correlation.
    variant : str
        Algorithm variant. Can be: 'cb', 'lgbm', 'linear', or 'random_forest'

    Returns
    -------
    Denoised image : numpy.ndarray

    """
    # Turn on Aydin's logging:
    from aydin.util.log.log import Log
    Log.enable_output = True

    # Import Aydin:
    from aydin.restoration.denoise.noise2selffgr import Noise2SelfFGR

    # Run N2S and save the result
    n2s = Noise2SelfFGR(variant=variant)

    # Train
    n2s.train(image, batch_axes=batch_axes, chan_axes=chan_axes)

    # Denoise
    denoised = n2s.denoise(image, batch_axes=batch_axes, chan_axes=chan_axes)

    # Turn off Aydin's logging:
    Log.enable_output = False

    return denoised

