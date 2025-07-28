### SIGNATURE


def aydin_classic_denoising(image, batch_axes=None, chan_axes=None, variant=None):
    """
    Denoise an image using Aydin's Classic restoration algorithms.
    
    Applies the specified variant of Aydin's Classic denoising to the input image, optionally considering batch and channel axes.
    
    Parameters:
        image (numpy.ndarray): The noisy image to be denoised.
        batch_axes (array-like, optional): Indices of batch axes where no spatiotemporal correlation exists.
        chan_axes (array-like, optional): Indices of channel axes representing image channels.
        variant (str, optional): The denoising algorithm variant to use. Supported values include 'bilateral', 'butterworth', 'gaussian', 'gm', 'harmonic', 'nlm', 'pca', 'spectral', 'tv', and 'wavelet'.
    
    Returns:
        numpy.ndarray: The denoised image.
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
