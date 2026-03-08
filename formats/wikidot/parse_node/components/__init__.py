from .AIM import parse_aim
from .html5player import parse_html5player
from .image_block import parse_image_block, parse_image_block_adv
from .tabview import parse_tabview
from .user import parse_user, parse_user_adv
from .email_example import parse_email_example
from .collapsible import parse_collapsible
from .ACS import parse_acs
from .page_note import parse_page_note
from .login_logout import parse_login_logout
from .div import parse_div_block
from .CSS import parse_css_module
from .basalt_and_inject import (
    parse_theme_basalt, parse_license, parse_toc, parse_footnote, 
    parse_hr, parse_raisa_notice, parse_class_warning
)

COMPONENT_PARSERS = {
    'aim': parse_aim,
    'html5player': parse_html5player,
    'image-block': parse_image_block,
    'image-block-adv': parse_image_block_adv,
    'tabview': parse_tabview,
    'user': parse_user,
    'user-adv': parse_user_adv,
    'email-example': parse_email_example,
    'collapsible': parse_collapsible,
    'acs': parse_acs,
    'page-note': parse_page_note,
    'login-logout': parse_login_logout,
    'div-block': parse_div_block,
    'css-module': parse_css_module,
    'theme-basalt': parse_theme_basalt,
    'license': parse_license,
    'toc': parse_toc,
    'footnote': parse_footnote,
    'hr': parse_hr,
    'raisa-notice': parse_raisa_notice,
    'class-warning': parse_class_warning
}
