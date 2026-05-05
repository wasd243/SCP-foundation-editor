pub struct AcsInput {
    pub item: String,
    pub clearance_raw: String,
    pub secondary_raw: String,
    pub container_raw: String,
    pub secondary_icon_raw: String,
    pub disruption_raw: String,
    pub risk_raw: String,
    pub anim_checked: bool,
    pub shiver_checked: bool,
}

pub struct AcsData {
    pub item: String,
    pub clearance: String,
    pub container: String,
    pub secondary: String,
    pub secondary_icon: String,
    pub disruption: String,
    pub risk: String,
    pub anim_checked: bool,
    pub shiver_checked: bool,
}
