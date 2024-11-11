from . import books
from . import users
from . import comments
from . import ratings
from . import favorites

# Pro snazší import v hlavní aplikaci
__all__ = ['books', 'users', 'comments', 'ratings', 'favorites']