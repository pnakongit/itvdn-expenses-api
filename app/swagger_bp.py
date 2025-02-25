from flask_swagger_ui import get_swaggerui_blueprint

from app.config import BaseConfig

swagger_ui_bd = get_swaggerui_blueprint(
    base_url=BaseConfig.BASE_SWAGGER_URL,
    api_url=BaseConfig.SPEC_URL
)
