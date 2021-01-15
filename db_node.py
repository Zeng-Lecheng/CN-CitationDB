class Author:
    def __init__(self, **kwargs):
        if 'name' in kwargs:
            self.name: str = kwargs['name']
        if 'redirect_target' in kwargs:
            self.redirect_target: str = kwargs['redirect_target']
            return
        if 'title' in kwargs:
            self.title: list[str] = kwargs['title']
        if 'institution' in kwargs:
            self.institution: str = kwargs['institution']


class Title:
    def __init__(self, **kwargs):
        if 'name' in kwargs:
            self.name: str = kwargs['name']
        if 'sub_title' in kwargs:
            self.sub_title: list[str] = kwargs['sub_title']
