def on_bhl_toggled(on_bhl, toggled):
    if toggled:
        on_bhl.check_enable_basalt.setChecked(False)
        on_bhl.check_enable_shivering.setChecked(False)
        if not on_bhl.check_bhl_office.isChecked():
            on_bhl.check_bhl_office.setChecked(True)
        on_bhl.bhl_sub_options_frame.setEnabled(True)
    else:
        on_bhl.bhl_sub_options_frame.setEnabled(False)
    on_bhl.config_changed = True
    on_bhl.update_theme_state()