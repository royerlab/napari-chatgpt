from arbol import aprint

from napari_chatgpt.utils.network.port_available import is_port_available


def test_port_available():

    # Looks for the first port available after 9000 by looping through each port:
    available_port = None
    for port in range(9000, 10000):
        if is_port_available(port):
            aprint(f"Port {port} is available")
            available_port = port
            break


    if available_port is None:
        aprint("No port available between 5000 and 6000")

    else:
        # now start a simple server asynchronously on that port to occupy it:
        import asyncio
        from aiohttp import web

        # Define a simple handler that returns a simple response:
        async def handle(request):
            return web.Response(text="Hello, world")

        # Start the server:
        app = web.Application()
        app.router.add_get('/', handle)
        runner = web.AppRunner(app)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, 'localhost', available_port)

        # Start the server:
        loop.run_until_complete(site.start())
        aprint(f"Server started on port {available_port}")

        # Now check if the port is occupied:
        assert not is_port_available(available_port)

        # Clean up the server:
        loop.run_until_complete(site.stop())
        loop.run_until_complete(runner.cleanup())




