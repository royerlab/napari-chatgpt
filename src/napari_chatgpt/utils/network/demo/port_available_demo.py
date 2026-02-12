"""Demo script: start a simple HTTP server to test port-availability detection."""

# main to test automatic port increment in the omega server:
if __name__ == "__main__":
    # now start a simple server asynchronously on that port to occupy it:
    import asyncio

    from aiohttp import web

    # Define a simple handler that returns a simple response:
    async def handle(request):
        return web.Response(text="Hello, world")

    # Start the server:
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, "localhost", 9000)

        # Start the server:
        loop.run_until_complete(site.start())

        # wait until key pressed on terminal:
        input("Press Enter to continue...")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.close()
