from flask_swagger_ui import get_swaggerui_blueprint

from app import BASE_SWAGGER_URL, SPEC_URL

swagger_ui_bd = get_swaggerui_blueprint(
    base_url=BASE_SWAGGER_URL,
    api_url=SPEC_URL
)
