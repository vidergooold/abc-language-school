def test_app_module_imports_successfully():
    import app.main as main_module

    assert hasattr(main_module, "app")


def test_fastapi_app_instance_exists():
    from fastapi import FastAPI
    from app.main import app

    assert isinstance(app, FastAPI)


def test_key_router_paths_are_registered():
    from app.main import app

    paths = {route.path for route in app.routes}

    assert any(path.startswith("/api/v1/auth") for path in paths)
    assert any(path.startswith("/api/v1/messages") for path in paths)
    assert any(path.startswith("/api/v1/homeworks") for path in paths)
    assert any(path.startswith("/api/v1/schedule") for path in paths)
