# main to test automatic port increment in the omega server:
if __name__ == '__main__':
    import asyncio
    from aiohttp import web

    async def handle(request):
        return web.Response(text="Hello, world")

    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, 'localhost', 9000)
        loop.run_until_complete(site.start())
        input("Press Enter to continue...")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        loop.run_until_complete(runner.cleanup())
        loop.close()