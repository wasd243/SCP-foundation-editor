def on_basalt_toggled(on_basalt, toggled):
    if toggled:
        on_basalt.check_enable_shivering.setChecked(False)
        on_basalt.check_enable_bhl.setChecked(False)
        on_basalt.basalt_sub_options_frame.setEnabled(True)
    else:
        on_basalt.basalt_sub_options_frame.setEnabled(False)
    on_basalt.update_theme_state()