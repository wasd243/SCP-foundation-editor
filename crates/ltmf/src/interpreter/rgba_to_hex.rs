pub fn color_to_wikidot_hex(color: &str) -> Result<String, String> {
    let color = color.trim();

    if let Some(hex) = color.strip_prefix('#') {
        return Ok(hex.to_uppercase());
    }

    if let Some(values) = color
        .strip_prefix("rgb(")
        .and_then(|value| value.strip_suffix(')'))
    {
        let values = parse_color_values(values)?;
        if values.len() != 3 {
            return Err(format!("rgb color expected 3 values: {color}"));
        }

        return Ok(format!(
            "{:02X}{:02X}{:02X}",
            values[0] as u8,
            values[1] as u8,
            values[2] as u8
        ));
    }

    if let Some(values) = color
        .strip_prefix("rgba(")
        .and_then(|value| value.strip_suffix(')'))
    {
        let values = parse_color_values(values)?;
        if values.len() != 4 {
            return Err(format!("rgba color expected 4 values: {color}"));
        }

        let alpha = alpha_to_u8(values[3]);

        return Ok(format!(
            "{:02X}{:02X}{:02X}({:02X})",
            values[0] as u8,
            values[1] as u8,
            values[2] as u8,
            alpha
        ));
    }

    Err(format!("unsupported color format: {color}"))
}

fn parse_color_values(values: &str) -> Result<Vec<f32>, String> {
    values
        .split(',')
        .map(|value| {
            value
                .trim()
                .parse::<f32>()
                .map_err(|error| error.to_string())
        })
        .collect()
}

fn alpha_to_u8(alpha: f32) -> u8 {
    if alpha <= 1.0 {
        (alpha * 255.0).round() as u8
    } else {
        alpha.round() as u8
    }
}
