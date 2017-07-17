def init_endpoints(app):
    from .resources import init_route as res_init_routes

    catalog = [
        res_init_routes(app),
    ]

    endpoint = []

    for tr in catalog:
        for r in tr:
            endpoint.append(r)

    return endpoint
