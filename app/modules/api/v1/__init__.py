from . import resources

catalog = [
    resources.routes,
]

endpoint = []

for tr in catalog:
    for r in tr:
        endpoint.append(r)
