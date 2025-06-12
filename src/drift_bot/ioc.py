from dishka import Provider, provide, Scope, from_context, make_async_container


class AppProvider(Provider):
    ...


container = make_async_container(AppProvider())
