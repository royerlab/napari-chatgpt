### SIGNATURE
def aydin_fgr_denoising(image, batch_axes=None, chan_axes=None, variant=None):
    """
    Denoise an image using Aydin's Noise2Self FGR (Feature Generation and Regression) method.
    
    Parameters:
    	image (numpy.ndarray): The input image to be denoised.
    	batch_axes (array-like, optional): Indices of batch axes where no spatiotemporal correlation exists.
    	chan_axes (array-like, optional): Indices of channel axes corresponding to image channels.
    	variant (str, optional): Specifies the algorithm variant to use; options include 'cb', 'lgbm', 'linear', or 'random_forest'.
    
    Returns:
    	numpy.ndarray: The denoised image.
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
