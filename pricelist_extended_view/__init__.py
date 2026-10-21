# -*- coding: utf-8 -*-
from . import models
from . import views
from . import static

import logging

_logger = logging.getLogger(__name__)


def enable_pricelist_setting(env):

    _logger.warning(
        "========== ENABLE PRICELIST =========="
    )

    Settings = env['res.config.settings'].sudo()

    values = Settings.default_get(list(Settings._fields))

    values['group_product_pricelist'] = True

    settings = Settings.create(values)
    settings.execute()
