class Author:
    def __init__(self, **kwargs):
        self.name: str = kwargs['name']
        self.redirect_target: str = kwargs.get('redirect_target')
        if self.redirect_target is not None:
            return
        self.title: list[str] = kwargs.get('title', [])
        self.institution: str = kwargs.get('institution', '')
        self.ref_link: str = kwargs.get('ref_link', '')


class Title:
    def __init__(self, **kwargs):
        self.name: str = kwargs['name']
        self.redirect_target: str = kwargs.get('redirect_target')
        if self.redirect_target is not None:
            return
        self.sub_title: list[str] = kwargs.get('sub_title', [])
        self.author: list[str] = kwargs.get('author', [])
