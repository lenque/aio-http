from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from app import create_app


class AppTestCase(AioHTTPTestCase):

    async def get_application(self):
        app = create_app()
        if __name__ == '__main__':
            await web.run_app(app)
        return app

    @unittest_run_loop
    async def test_hello(self):
        resp = await self.client.request("GET", "/")
        assert resp.status == 200
        text = await resp.text()
        assert "horrible" in text

    # @unittest_run_loop
    # async def test_users(self):
    #     resp = await self.client.request("GET", "/users")
    #     assert resp.status == 200
    #     text = await resp.text()
    #     assert "horrible" in text