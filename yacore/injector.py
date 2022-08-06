from giveme import Injector

__all__ = (
    "injector",
    "inject",
    "register",
)

injector = Injector()
inject = injector.inject
register = injector.register
