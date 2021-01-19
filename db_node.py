class Author:
    def __init__(self, **kwargs):
        self.name: str = kwargs['name']
        self.redirect_target: str = kwargs.get('redirect_target', '')
        self.title: list[str] = kwargs.get('title', [])
        self.institution: str = kwargs.get('institution', '')
        self.ref_link: str = kwargs.get('ref_link', '')


class Title:
    def __init__(self, **kwargs):
        self.name: str = kwargs['name']
        self.redirect_target: str = kwargs.get('redirect_target', '')
        self.sub_title: list[str] = kwargs.get('sub_title', [])
        self.author: list[str] = kwargs.get('author', [])
