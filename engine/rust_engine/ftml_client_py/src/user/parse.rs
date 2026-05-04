use super::model::{UserData, UserKind};

pub fn parse_basic_user(name: &str) -> UserData {
    UserData {
        name: name.trim().to_string(),
        kind: UserKind::Basic,
    }
}

pub fn parse_advanced_user(name: &str) -> UserData {
    UserData {
        name: name.trim().to_string(),
        kind: UserKind::Advanced,
    }
}
