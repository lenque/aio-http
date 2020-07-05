import pathlib
import aiohttp
import yaml
import asyncpgsa
from aiohttp import web
from sqlalchemy import select, insert, and_
routes = web.RouteTableDef()

# ______________________________
# 2.SQL EXPRESSION
from models import users, cars

# users
# @routes.post('/users')
async def post_user(request):
    try:
        data = await request.json()
        async with request.app['db'].acquire() as conn:
            # all_columns = [column.name for column in users.columns]
            all_columns = users.columns.keys()
            res = {}
            for c in all_columns:
                if c != 'id':
                    try:
                        res[c] = data[c]
                    except Exception:
                        return aiohttp.web.HTTPBadRequest(text=f'param {c.upper()} is required')
            await conn.execute(users.insert().values(res))
            # await conn.execute(users.insert({'name': data['name'], 'surname': data['surname'],
            # 'patronymic': data['patronymic'], 'gender': data['gender'], 'age': data['age']}))
            return aiohttp.web.HTTPCreated()
    except Exception:
        return aiohttp.web.HTTPBadRequest()


# @routes.get('/users/{user_id}')
async def get_user(request):
    try:
        user_id = int(request.match_info.get('user_id'))
        async with request.app['db'].acquire() as conn:
            # print(conn.__dir__())
            raw_query = await conn.fetchrow(users.select().where(users.c.id == user_id))
            return web.json_response(dict(raw_query))
    except Exception:
        return aiohttp.web.HTTPNotFound()


# @routes.get('/users')
async def get_all_users(request):
    async with request.app['db'].acquire() as conn:
        raw_query = await conn.fetch(users.select().order_by(users.c.surname))
        query = [dict(record) for record in raw_query]
        if query:
            return web.json_response(query)
        else:
            return aiohttp.web.HTTPNoContent()


# @routes.post('/users/filter')
async def select_user(request):
    try:
        data = await request.json()
        async with request.app['db'].acquire() as conn:
            all_columns = users.columns.keys()
            for key in data.keys():
                if key not in all_columns or not data[key]:
                    return aiohttp.web.HTTPBadRequest(text=f'not valid param {key.upper()}')
            raw_query = await conn.fetch(
                users.select().where((and_(users.c.name == data['name'], users.c.surname == data['surname'],
                                     users.c.patronymic == data['patronymic'], users.c.gender == data['gender']))))
            if raw_query:
                query = [dict(record) for record in raw_query]
                return web.json_response(query)
            else:
                return aiohttp.web.HTTPNoContent()
    except Exception:
        return aiohttp.web.HTTPNotFound()


# @routes.put('/users')
async def update_user(request):
    try:
        data = await request.json()
        async with request.app['db'].acquire() as conn:
            all_columns = users.columns.keys()
            for key in data.keys():
                if key not in all_columns or not data[key]:
                    return aiohttp.web.HTTPBadRequest(text=f'not valid param {key.upper()}')
            raw_query = await conn.fetch(
                users.update().where(users.c.id == int(data['id'])).values(surname=data['surname'],
                                                                           patronymic=data['patronymic'],
                                                                           gender=data['gender']))
            return aiohttp.web.HTTPCreated()
    except Exception:
        return aiohttp.web.HTTPBadRequest()


# cars
# @routes.get('/cars')
async def get_all_cars(request):
    async with request.app['db'].acquire() as conn:
        raw_query = await conn.fetch(cars.select())
        query = [dict(record) for record in raw_query]
        if query:
            return web.json_response(query)
        else:
            return aiohttp.web.HTTPNoContent()


# @routes.post('/cars')
async def post_car(request):
    try:
        data = await request.json()
        async with request.app['db'].acquire() as conn:
            user = data['user_id']
            raw_user = await conn.fetchrow(users.select(users.c.id == user))
            if not raw_user:
                return aiohttp.web.HTTPBadRequest(text=f'no such user')
            all_columns = cars.columns.keys()
            res = {}
            for c in all_columns:
                if c != 'id':
                    try:
                        res[c] = data[c]
                    except Exception:
                        return aiohttp.web.HTTPBadRequest(text=f'param {c.upper()} is required')
            r = await conn.execute(cars.insert().values(res))
            return aiohttp.web.HTTPCreated()
    except Exception:
        return aiohttp.web.HTTPBadRequest()


# @routes.get('/cars/{car_id}')
async def get_car(request):
    try:
        car_id = int(request.match_info.get('car_id'))
        async with request.app['db'].acquire() as conn:
            raw_query = await conn.fetchrow(cars.select(cars.c.id == car_id))
            return web.json_response(dict(raw_query))
    except Exception:
        return aiohttp.web.HTTPNotFound()


# @routes.put('/cars')
async def update_car(request):
    try:
        data = await request.json()
        async with request.app['db'].acquire() as conn:
            all_columns = cars.columns.keys()
            for key in data.keys():
                if key not in all_columns or not data[key]:
                    return aiohttp.web.HTTPBadRequest(text=f'not valid param {key.upper()}')
            raw_query = await conn.fetch(
                cars.update().where(cars.c.id == int(data['id'])).values(model=data['model'], color=data['color']))
            return aiohttp.web.HTTPCreated()
    except Exception:
        return aiohttp.web.HTTPBadRequest()


# @routes.get('/user-cars/{user_id}')
async def get_user_car(request):
    try:
        user_id = int(request.match_info.get('user_id'))
        async with request.app['db'].acquire() as conn:
            j = users.join(cars, users.c.id == cars.c.user_id)
            raw_query = await conn.fetch(select([users, cars]).select_from(j).where(users.c.id == user_id))
            if raw_query:
                query = [dict(record) for record in raw_query]
                return web.json_response(query)
            else:
                return aiohttp.web.HTTPNoContent()
    except Exception:
        return aiohttp.web.HTTPBadRequest()


# ______________________________
# 3.SQL ORM
# from models import User
#
#
# @routes.post('/users')
# async def post_users(request):
#     data = await request.json()
#     async with request.app['db'].acquire() as conn:
#         print(User.__table__)
#         query = await conn.execute(User.__table__.insert().values(name=data['name'], surname=data['surname'],
#                                                                   patronymic=data['patronymic'],
#                                                                   gender=data['gender'],
#                                                                   age=data['age']))
#     return aiohttp.web.HTTPCreated()
#
#
# @routes.get('/users')
# async def get_all_users(request):
#     async with request.app['db'].acquire() as conn:
#         raw_query = await conn.fetch(select([User]))
#         # query = [User.to_json(dict(record)) for record in raw_query]
#         query = [dict(record) for record in raw_query]
#     return web.json_response(query, status=200)

# ______________________________
# ROUTES
def set_routes(app):
    app.router.add_get('/', hello)

    app.router.add_post('/users', post_user)
    app.router.add_get('/users/{user_id}', get_user)
    app.router.add_get('/users', get_all_users)
    app.router.add_get('//users/filter', select_user)
    app.router.add_put('/users', update_user)

    app.router.add_get('/cars', get_all_cars)
    app.router.add_post('/cars', post_car)
    app.router.add_get('/cars/{car_id}', get_car)
    app.router.add_put('/cars', update_car)

    app.router.add_get('/user-cars/{user_id}', get_user_car)

# ______________________________
# APPLICATION
# test handler for config from yaml
@routes.get('/')
async def hello(request):
    project_name = request.app['config'].get('project_name')
    return web.Response(text=f"This is a horrible {project_name} :)")


# load & read (+rewrite) configuration file
def load_config(config_file=None):
    default_file = pathlib.Path(__file__).parent / 'config.yaml'
    with open(default_file, 'r') as f:
        config = yaml.safe_load(f)
    conf_dict = {}
    if config_file:
        conf_dict = yaml.safe_load(config_file)
        config.update(**conf_dict)
    return config


# connect db
async def on_start(app):
    config = app['config']
    app['db'] = await asyncpgsa.create_pool(dsn=config['db'])


# disconnect db
async def on_leave(app):
    await app['db'].close()


# create app
def create_app():
    app = web.Application()
    # app.add_routes(routes)
    set_routes(app)
    app['config'] = load_config()
    app.on_startup.append(on_start)
    app.on_cleanup.append(on_leave)
    return app


app = create_app()

if __name__ == '__main__':
    web.run_app(app, port=8081)

# ______________________________
# NOTES for me
# # acquire() blocks until a call to release() in another thread changes it to unlocked,
# # then the acquire() call resets it to locked and returns.
# # acquire() захват блокировки процесса
# # a coroutine that accepts a Request instance (as its only parameter) and returns a Response instance
#
# SNAP=true /snap/postman/current/usr/share/Postman/Postman
