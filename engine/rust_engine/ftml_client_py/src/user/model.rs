#[derive(Debug, Clone)]
pub enum UserKind {
    Basic,
    Advanced,
}

#[derive(Debug, Clone)]
pub struct UserData {
    pub name: String,
    pub kind: UserKind,
}
