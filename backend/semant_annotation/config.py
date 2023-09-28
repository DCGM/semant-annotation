import os


class Config:
    def __init__(self):
        self.UPLOADED_IMAGES_FOLDER = os.getenv("UPLOADED_IMAGES_PATH", './uploaded_images')
        self.PREVIEW_IMAGES_FOLDER = os.getenv("PREVIEW_PATH", './previews')
        self.SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:policko05@localhost:5432/semant_annotation-dev")
        self.SECRET_KEY = os.getenv("SECRET_KEY", 't3qX7x4U3A0lFG0ea8E8KPSI4L7GrUlx')
        self.HASH_ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 120
        self.ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "semant")
        self.ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "semant")
        self.PRODUCTION = os.getenv("PRODUCTION", False)
        self.PREVIEW_RESOLUTION = int(os.getenv("PREVIEW_RESOLUTION", 320))
        self.JSON_SORT_KEYS = False

    def create_dirs(self):
        os.makedirs(self.PREVIEW_IMAGES_FOLDER, exist_ok=True)
        os.makedirs(self.PREVIEW_IMAGES_FOLDER, exist_ok=True)


config = Config()
config.create_dirs()

