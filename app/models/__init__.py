from .categories import Category
from .courses import Course
from .users import User

User.model_rebuild()
Course.model_rebuild()
Category.model_rebuild()
