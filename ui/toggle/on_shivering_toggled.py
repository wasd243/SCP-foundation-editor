def on_shivering_toggled(on_shivering, toggled):
    if toggled:
        on_shivering.check_enable_basalt.setChecked(False)
        on_shivering.check_enable_bhl.setChecked(False)
        on_shivering.shivering_sub_options_frame.setEnabled(True)
    else:
        on_shivering.shivering_sub_options_frame.setEnabled(False)
    on_shivering.update_theme_state()