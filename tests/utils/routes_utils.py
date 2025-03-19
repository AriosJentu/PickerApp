from tests.utils.types import Routes

def get_protected_routes(all_routes: Routes) -> Routes:
    return [
        (method, url, roles)
        for (method, url, roles) in all_routes
        if roles is not None
    ]
